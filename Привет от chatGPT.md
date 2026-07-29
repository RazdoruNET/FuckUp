Комплексный инструмент тестирования сетевой инфраструктуры от chatGPT

```python
import asyncio
import time
import logging
from typing import List, Dict, Any, Protocol, runtime_checkable
from dataclasses import dataclass, field
import dns.asyncresolver
from pysnmp.hlapi.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    getCmd
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [AsyncCore] %(message)s",
    handlers=[logging.StreamHandler()]
)

@dataclass
class TargetContext:
    role: str
    criticality: int

@dataclass
class EnvironmentScope:
    allowed_subnets: List[str]
    rate_limit_rps: float
    environment_tier: str

class TelemetryCollector:
    def __init__(self):
        self._metrics: Dict[str, List[float]] = {}
        self._lock = asyncio.Lock()

    async def record_latency(self, plugin_name: str, duration: float):
        async with self._lock:
            self._metrics.setdefault(f"{plugin_name}_latency", []).append(duration)

    async def record_error(self, plugin_name: str):
        async with self._lock:
            self._metrics.setdefault(f"{plugin_name}_errors", []).append(1.0)

    def export_metrics(self) -> Dict[str, Any]:
        summary = {}
        for k, v in self._metrics.items():
            summary[k] = {"count": len(v), "avg": sum(v) / len(v) if v else 0.0}
        return summary

@runtime_checkable
class SecurityPlugin(Protocol):
    name: str
    async def execute(self, target_ip: str, context: TargetContext, telemetry: TelemetryCollector) -> Dict[str, Any]:
        ...

class AsynchronousDNSProbePlugin:
    name = "dns_recursion_probe"

    async def execute(self, target_ip: str, context: TargetContext, telemetry: TelemetryCollector) -> Dict[str, Any]:
        start_time = time.perf_counter()
        resolver = dns.asyncresolver.Resolver()
        resolver.nameservers = [target_ip]
        resolver.timeout = 1.5
        resolver.lifetime = 1.5

        is_open = False
        try:
            answers = await resolver.resolve('iana.org', 'A')
            if answers:
                is_open = True
            duration = time.perf_counter() - start_time
            await telemetry.record_latency(self.name, duration)
        except Exception:
            await telemetry.record_error(self.name)
            
        return {"dns_open_resolver": is_open}

class AsynchronousSNMPProbePlugin:
    name = "snmp_exposure_probe"

    async def execute(self, target_ip: str, context: TargetContext, telemetry: TelemetryCollector) -> Dict[str, Any]:
        start_time = time.perf_counter()
        exposed = False
        
        try:
            error_indication, error_status, error_index, var_binds = await getCmd(
                SnmpEngine(),
                CommunityData('public', mpModel=0),
                UdpTransportTarget((target_ip, 161), timeout=1.0, retries=1),
                ContextData(),
                ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0'))
            )
            if not error_indication and not error_status:
                exposed = True
            
            duration = time.perf_counter() - start_time
            await telemetry.record_latency(self.name, duration)
        except Exception:
            await telemetry.record_error(self.name)

        return {"snmp_public": exposed}

class AdvancedRiskAnalyzer:
    WEIGHTS = {
        "dns_open_resolver": 25,
        "snmp_public": 60,
        "snmp_v2": 20
    }

    def evaluate(self, accumulated_data: Dict[str, Any], context: TargetContext) -> Dict[str, Any]:
        base_score = sum(
            self.WEIGHTS[k] for k, v in accumulated_data.items() if v and k in self.WEIGHTS
        )
        
        final_score = int(base_score * context.criticality)
        level = self._determine_level(final_score)
        
        return {
            "score": final_score,
            "level": level,
            "confidence": 0.92 if context.role in ["edge", "core"] else 0.75
        }

    @staticmethod
    def _determine_level(score: int) -> str:
        if score > 120:
            return "CRITICAL"
        elif score > 60:
            return "HIGH"
        elif score > 20:
            return "MEDIUM"
        return "LOW"

class EnterpriseAsyncSecurityOrchestrator:
    def __init__(self, scope: EnvironmentScope):
        self.scope = scope
        self.plugins: List[SecurityPlugin] = []
        self.telemetry = TelemetryCollector()
        self.risk_engine = AdvancedRiskAnalyzer()

    def register_plugin(self, plugin: SecurityPlugin):
        self.plugins.append(plugin)

    async def dispatch_assessment(self, target_ip: str, context: TargetContext) -> Dict[str, Any]:
        logging.info(f"Начало асинхронного аудита для хоста {target_ip} [Роль: {context.role}, Критичность: {context.criticality}]")
        
        aggregated_findings: Dict[str, Any] = {}
        tasks = [plugin.execute(target_ip, context, self.telemetry) for plugin in self.plugins]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for res in results:
            if isinstance(res, dict):
                aggregated_findings.update(res)

        risk_assessment = self.risk_engine.evaluate(aggregated_findings, context)
        
        return {
            "target": target_ip,
            "context": {"role": context.role, "criticality": context.criticality},
            "findings": aggregated_findings,
            "risk_model": risk_assessment,
            "telemetry": self.telemetry.export_metrics()
        }

if __name__ == "__main__":
    async def main():
        scope = EnvironmentScope(
            allowed_subnets=["78.37.77.0/24", "100.76.128.0/24"],
            rate_limit_rps=50.0,
            environment_tier="ENTERPRISE_PROD"
        )
        
        orchestrator = EnterpriseAsyncSecurityOrchestrator(scope)
        orchestrator.register_plugin(AsynchronousDNSProbePlugin())
        orchestrator.register_plugin(AsynchronousSNMPProbePlugin())
        
        target_context = TargetContext(role="edge", criticality=2)
        
        # report = await orchestrator.dispatch_assessment("78.37.77.77", target_context)
        # print(report)

    # asyncio.run(main())

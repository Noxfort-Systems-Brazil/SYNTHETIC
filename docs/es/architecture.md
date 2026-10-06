# 🏛️ SYNTHETIC: Arquitectura del Sistema y Blueprint de Ejecución

Este documento especifica la arquitectura técnica del ecosistema **SYNTHETIC**, motor corporativo de IA generativa diseñado para la síntesis de escenarios de tráfico multimodal urbano de alta fidelidad. Detalla el pipeline en dos fases, la gestión dinámica de memoria mediante carga secuencial bajo demanda (Lazy Loading) y la separación estricta entre leyes físicas y percepción sensorial.

⬅️ [Centro de Documentación](README.md) | 🧠 [IA Generativa y Física](generative_ai_and_physics.md) | 📡 [Generadores Multimodales](multimodal_generators.md) | 🧪 [Pruebas y QA](testing.md)

---

## 1. Filosofía de Arquitectura y Principios

1. **Separación Estricta entre Física Real y Percepción Sensorial:** En el mundo físico, las leyes de la cinemática no fallan. Los vehículos no se teletransportan y la inercia se respeta. Sin embargo, los sensores (sondas GPS, espiras inductivas, cámaras) fallan constantemente debido a ruido electromagnético, pérdidas de red y anomalías. SYNTHETIC sintetiza primero una simulación física matemáticamente exacta y luego inyecta deliberadamente una capa realista de corrupción sensorial.
2. **Liberación Secuencial de Recursos (Cero Desperdicio de VRAM):** Redes de gran escala (Phi-4 SLM, VAE-TCN, Difusión CSDI, GATv2) nunca coexisten en la memoria GPU. Cada modelo se carga exclusivamente durante su fase de inferencia y se purga de inmediato mediante `gc.collect()` y limpieza de caché CUDA.
3. **Principio de Responsabilidad Única (SRP):** El razonamiento cognitivo se delega al Guionista (Screenwriter), la validación de límites físicos al Director, la topología urbana a GATv2 y la dinámica meteorológica al motor de Markov.

---

## 2. Ciclo de Vida de Generación en Dos Fases

```mermaid
sequenceDiagram
    autonumber
    participant ENV as EnvironmentManager
    participant M as SimulationOrchestrator (Maestro)
    participant S as ScreenwriterAgent (Phi-4)
    participant D as DirectorAgent
    participant V as Guardián VAE-TCN
    participant C as Motor de Difusión CSDI
    participant GEN as Generadores Multimodales

    Note over ENV,M: Etapa de Inicialización
    ENV->>M: Ground Zero Temporal (Lunes 00:00:00) & Semilla Climática
    
    rect rgb(240, 248, 255)
    Note over M,S: FASE 1: Sueño Cognitivo (SLM Activo)
    M->>S: Restricciones Diarias (Clima Markov, Calendario, Densidad)
    S->>S: Razonamiento Interno Profundo (Modo <think>)
    S->>M: Vector Latente de 2048 Dimensiones por Día
    Note over S: Recolección Explícita de Basura & Purga VRAM
    end

    rect rgb(255, 245, 238)
    Note over D,GEN: FASE 2: Física & Síntesis Multimodal (Bucle por Día)
    loop Cada Día de Simulación
        M->>D: Vector Latente Diario + Contexto Topológico OSM
        D->>V: Validación de Realismo Físico y Clamping
        V-->>D: Tensor Físico Validado en Variedad (20-110 km/h)
        Note over V: Purga de VAE-TCN de VRAM
        D->>C: Difusión Inversa Condicionada (con Buffer Seed Tail)
        C-->>D: Series Temporales Continuas de Velocidad y Flujo
        Note over C: Purga de CSDI de VRAM
        D->>GEN: Matrices Físicas Reales (Ground Truth)
        GEN->>GEN: Inyección de Fallas, Dropouts y Ruido de Sensores
        GEN->>M: Escritura Final de Feeds JSON/CSV en Disco
    end
    end
```

---

<div align="center">
  <img src="../assets/noxfort-logo.png" alt="Noxfort Systems Logo" width="45" /><br/>
  <b>Noxfort Systems</b> — <i>A State Of Art Company</i>
</div>

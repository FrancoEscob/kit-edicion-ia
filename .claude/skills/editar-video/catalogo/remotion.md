# Remotion

Remotion es la alternativa a HyperFrames: la misma idea (código que se renderiza a video), pero escrita en React. Solo se instala si la persona lo pide: `npx -y skills add remotion-dev/skills`.

- **Cuándo elegirlo:** si la persona ya sabe React, quiere componentes reutilizables con propiedades, o ya tiene un proyecto en Remotion.
- **Licencia:** gratis para personas y equipos de hasta 3. Una empresa más grande necesita la licencia de empresa. Avisalo una vez al instalarlo.
- **Estructura del montaje:** la misma de `montar-video`: la persona (`<OffthreadVideo>`), escenas de corte (`<Sequence>`), gráficos encima, subtítulos y audio. Los tiempos salen de `base-palabras.json`, pasados a cuadros (`Math.round(segundos * fps)`).
- **Estilos:** los del kit (`estilos/`) y la estética de Lemo se aplican igual que en HyperFrames; cambia solo el código.
- **Ejemplos y plantillas:** https://www.remotion.dev/templates y las reglas de sus skills.

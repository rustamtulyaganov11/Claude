import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const FONT = "Inter, 'DejaVu Sans', sans-serif";
const ACCENT = "#7c5cff";

const PLUGINS = [
  { name: "Remotion", desc: "видео из кода" },
  { name: "Figma", desc: "макеты в код" },
  { name: "Frontend Design", desc: "красивые интерфейсы" },
  { name: "Claude-Mem", desc: "память между сессиями" },
  { name: "Claude Code Setup", desc: "настройка проекта" },
];

const Background: React.FC = () => {
  const frame = useCurrentFrame();
  const angle = interpolate(frame, [0, 360], [140, 220]);
  const x = 50 + Math.sin(frame / 40) * 20;
  const y = 30 + Math.cos(frame / 50) * 15;
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(circle at ${x}% ${y}%, rgba(124,92,255,0.55), transparent 55%),
          linear-gradient(${angle}deg, #0b0b1a, #161033 60%, #0b0b1a)`,
      }}
    />
  );
};

const Title: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 12 } });
  const sub = interpolate(frame, [20, 40], [0, 1], { extrapolateRight: "clamp" });
  const out = interpolate(frame, [75, 90], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: out }}>
      <div
        style={{
          fontFamily: FONT,
          fontSize: 130,
          fontWeight: 800,
          color: "white",
          textAlign: "center",
          lineHeight: 1.05,
          transform: `scale(${pop})`,
        }}
      >
        Пробный
        <br />
        <span style={{ color: ACCENT }}>ролик</span>
      </div>
      <div
        style={{
          fontFamily: FONT,
          fontSize: 48,
          color: "rgba(255,255,255,0.75)",
          marginTop: 40,
          opacity: sub,
          transform: `translateY(${(1 - sub) * 30}px)`,
        }}
      >
        сделано кодом в Remotion
      </div>
    </AbsoluteFill>
  );
};

const PluginList: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const out = interpolate(frame, [135, 150], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ padding: 90, justifyContent: "center", opacity: out }}>
      <div style={{ fontFamily: FONT, fontSize: 72, fontWeight: 800, color: "white", marginBottom: 60 }}>
        Установленные плагины
      </div>
      {PLUGINS.map((p, i) => {
        const s = spring({ frame: frame - 10 - i * 10, fps, config: { damping: 14 } });
        return (
          <div
            key={p.name}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 36,
              marginBottom: 34,
              padding: "34px 40px",
              borderRadius: 32,
              background: "rgba(255,255,255,0.08)",
              border: "2px solid rgba(255,255,255,0.12)",
              opacity: s,
              transform: `translateX(${(1 - s) * -200}px)`,
            }}
          >
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: 40,
                background: ACCENT,
                color: "white",
                fontFamily: FONT,
                fontSize: 44,
                fontWeight: 800,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              {i + 1}
            </div>
            <div style={{ fontFamily: FONT }}>
              <div style={{ fontSize: 54, fontWeight: 700, color: "white" }}>{p.name}</div>
              <div style={{ fontSize: 38, color: "rgba(255,255,255,0.65)" }}>{p.desc}</div>
            </div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

const Outro: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pop = spring({ frame, fps, config: { damping: 10 } });
  const bar = interpolate(frame, [10, 90], [0, 100], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          fontFamily: FONT,
          fontSize: 110,
          fontWeight: 800,
          color: "white",
          transform: `scale(${pop})`,
        }}
      >
        Готово!
      </div>
      <div style={{ fontFamily: FONT, fontSize: 46, color: "rgba(255,255,255,0.75)", marginTop: 30 }}>
        Claude Code × Remotion
      </div>
      <div
        style={{
          width: 700,
          height: 14,
          borderRadius: 7,
          background: "rgba(255,255,255,0.15)",
          marginTop: 70,
          overflow: "hidden",
        }}
      >
        <div style={{ width: `${bar}%`, height: "100%", background: ACCENT }} />
      </div>
    </AbsoluteFill>
  );
};

export const Demo: React.FC = () => (
  <AbsoluteFill>
    <Background />
    <Sequence durationInFrames={90}>
      <Title />
    </Sequence>
    <Sequence from={90} durationInFrames={150}>
      <PluginList />
    </Sequence>
    <Sequence from={240}>
      <Outro />
    </Sequence>
  </AbsoluteFill>
);

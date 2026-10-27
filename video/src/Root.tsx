import { Composition } from "remotion";
import { Demo } from "./Demo";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Demo"
    component={Demo}
    durationInFrames={360}
    fps={30}
    width={1080}
    height={1920}
  />
);

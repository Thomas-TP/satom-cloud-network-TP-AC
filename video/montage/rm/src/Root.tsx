import React from 'react';
import {AbsoluteFill, Audio, Composition, Sequence} from 'remotion';
import data from './data.json';
import {Gui} from './Gui';
import {Chapter, Diagram, End, Title} from './Cards';

const Main: React.FC = () => {
  const sc: any[] = (data as any).scenes;
  return (
    <AbsoluteFill style={{background: '#0b1020'}}>
      {(data as any).audio && <Audio src={(data as any).audio} />}
      {sc.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={s.dur} layout="none">
          <Sequence from={0} durationInFrames={s.dur} name={s.id || s.type}>
            <AbsoluteFill>
              {s.type === 'title' && <Title dur={s.dur} />}
              {s.type === 'intro' && <Diagram img={s.img} dur={s.dur} label="Le projet" sub="Un réseau complet : siège, agence et cloud" focus={s.focus} />}
              {s.type === 'chapter' && <Chapter mod={s.mod} img={s.img} dur={s.dur} />}
              {s.type === 'gui' && <Gui s={s} fadeIn={i > 0 ? (sc[i - 1].type === 'gui' ? 6 : 10) : 0} />}
              {s.type === 'end' && <End img={s.img} dur={s.dur} />}
            </AbsoluteFill>
          </Sequence>
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition id="Main" component={Main} durationInFrames={(data as any).total} fps={30} width={1920} height={1080} />
);

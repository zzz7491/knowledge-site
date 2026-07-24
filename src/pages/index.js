import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import clsx from 'clsx';
import styles from './index.module.css';

const tracks = [
  {
    index: '01',
    eyebrow: 'FRONTIER',
    title: '科技前沿',
    text: '跟踪 AI、智能体与云原生技术的关键变化，把噪音整理成可行动的认知。',
    link: '/docs/每日更新/2026-07-24-快报',
  },
  {
    index: '02',
    eyebrow: 'PRACTICE',
    title: '工程实践',
    text: '从架构、工具链到部署，把复杂技术拆成可以复现的步骤与方案。',
    link: '/docs/dev-guides/setup-guide',
  },
  {
    index: '03',
    eyebrow: 'DEEP DIVE',
    title: '深度知识',
    text: '围绕真正值得投入时间的问题，持续沉淀高密度、可检索的知识卡片。',
    link: '/docs/paid-knowledge/first-article',
  },
];

export default function Home() {
  return (
    <Layout title="首页" description="面向未来的科技知识库">
      <main className={styles.home}>
        <section className={styles.hero}>
          <div className={styles.heroGlow} aria-hidden="true" />
          <div className={styles.heroGrid} aria-hidden="true" />
          <div className={styles.heroContent}>
            <p className={styles.kicker}><span /> KNOWLEDGE SYSTEM / 2026</p>
            <h1>把复杂世界，<br /><em>整理成可用的知识。</em></h1>
            <p className={styles.heroText}>
              一个持续更新的科技知识系统。筛选前沿信号，拆解工程实践，
              为每一次学习和创造提供更清晰的下一步。
            </p>
            <div className={styles.heroActions}>
              <Link className={styles.primaryButton} to="/docs/paid-knowledge/first-article">
                进入知识库 <span>↗</span>
              </Link>
              <Link className={styles.textButton} to="/docs/intro">了解这个项目 <span>→</span></Link>
            </div>
          </div>
          <div className={styles.signalPanel} aria-label="系统状态">
            <div className={styles.signalHeader}><span className={styles.liveDot} /> SYSTEM ONLINE <span>实时</span></div>
            <div className={styles.signalVisual}>
              <div className={styles.signalRing} />
              <div className={styles.signalCore}>∞</div>
              <div className={clsx(styles.signalLabel, styles.signalLabelTop)}>CURATE</div>
              <div className={clsx(styles.signalLabel, styles.signalLabelRight)}>CONNECT</div>
              <div className={clsx(styles.signalLabel, styles.signalLabelBottom)}>CREATE</div>
            </div>
            <div className={styles.signalFooter}><span>持续更新</span><strong>●</strong><span>面向未来</span></div>
          </div>
        </section>

        <section className={styles.metrics} aria-label="知识库概览">
          <div><strong>01</strong><span>个知识入口</span></div>
          <div><strong>∞</strong><span>持续生长的想法</span></div>
          <div><strong>24/7</strong><span>随时可以访问</span></div>
          <p>Curiosity is a feature.</p>
        </section>

        <section className={styles.explore}>
          <div className={styles.sectionHeading}>
            <p className={styles.kicker}><span /> EXPLORE THE SYSTEM</p>
            <h2>从一个问题开始，<br />沿着知识继续深入。</h2>
          </div>
          <div className={styles.trackGrid}>
            {tracks.map((track) => (
              <Link className={styles.trackCard} to={track.link} key={track.index}>
                <div className={styles.trackTop}><span>{track.index}</span><span>↗</span></div>
                <p>{track.eyebrow}</p>
                <h3>{track.title}</h3>
                <div className={styles.trackBottom}><span>{track.text}</span><i /></div>
              </Link>
            ))}
          </div>
        </section>

        <section className={styles.manifesto}>
          <div className={styles.manifestoMark}>//</div>
          <div>
            <p className={styles.kicker}><span /> A NOTE FROM THE BUILDER</p>
            <h2>好的知识，不应该<br /><em>只停留在收藏夹里。</em></h2>
            <p>这里记录值得反复回看的内容，也记录正在形成中的判断。慢慢读，认真做，让知识真正发生连接。</p>
          </div>
          <Link className={styles.outlineButton} to="/docs/intro">查看项目说明 <span>↗</span></Link>
        </section>
      </main>
    </Layout>
  );
}

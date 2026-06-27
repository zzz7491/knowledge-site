import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function Home() {
  return (
    <Layout
      title="首页"
      description="知识付费分享平台"
    >
      <header style={{
        padding: '80px 20px',
        textAlign: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <h1 style={{ fontSize: '48px', marginBottom: '16px' }}>
          📚 我的知识库
        </h1>
        <p style={{ fontSize: '20px', opacity: 0.9 }}>
          精选付费知识内容，持续更新
        </p>
        <div style={{ marginTop: '32px' }}>
          <Link
            to="/docs/付费知识"
            style={{
              padding: '12px 32px',
              background: 'white',
              color: '#667eea',
              borderRadius: '8px',
              fontWeight: 'bold',
              textDecoration: 'none',
              marginRight: '12px'
            }}
          >
            开始学习
          </Link>
          <Link
            to="/login"
            style={{
              padding: '12px 32px',
              background: 'transparent',
              color: 'white',
              borderRadius: '8px',
              fontWeight: 'bold',
              textDecoration: 'none',
              border: '2px solid white'
            }}
          >
            登录 / 注册
          </Link>
        </div>
      </header>

      <section style={{ padding: '60px 20px', maxWidth: '900px', margin: '0 auto' }}>
        <h2 style={{ textAlign: 'center', fontSize: '32px' }}>✨ 内容特色</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px', marginTop: '40px' }}>
          <div style={{ textAlign: 'center', padding: '24px', border: '1px solid #e5e7eb', borderRadius: '12px' }}>
            <div style={{ fontSize: '40px' }}>📖</div>
            <h3>精选知识</h3>
            <p style={{ color: '#6b7280' }}>优质付费内容，持续更新</p>
          </div>
          <div style={{ textAlign: 'center', padding: '24px', border: '1px solid #e5e7eb', borderRadius: '12px' }}>
            <div style={{ fontSize: '40px' }}>💡</div>
            <h3>实战导向</h3>
            <p style={{ color: '#6b7280' }}>理论结合实践，学以致用</p>
          </div>
          <div style={{ textAlign: 'center', padding: '24px', border: '1px solid #e5e7eb', borderRadius: '12px' }}>
            <div style={{ fontSize: '40px' }}>🚀</div>
            <h3>持续更新</h3>
            <p style={{ color: '#6b7280' }}>每周新增内容，保持新鲜</p>
          </div>
        </div>
      </section>
    </Layout>
  );
}
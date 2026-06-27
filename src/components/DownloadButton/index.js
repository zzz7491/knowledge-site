import React, { useState } from 'react';

export default function DownloadButton({ fileKey, fileName, isPaid, price }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showPayment, setShowPayment] = useState(false);

  const handleDownload = async () => {
    if (!isPaid) {
      setShowPayment(true);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/download?file=${encodeURIComponent(fileKey)}`,
        {
          headers: {
            'Authorization': 'Bearer demo-token-123'
          }
        }
      );

      if (!response.ok) {
        const errText = await response.text();
        console.error('错误响应:', errText);
        throw new Error('下载失败');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName || fileKey.split('/').pop();
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (err) {
      setError(err.message);
      console.error('下载错误:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = (method) => {
    alert(`正在跳转到${method}支付，金额：¥${price}`);
    setShowPayment(false);
  };

  if (showPayment) {
    return (
      <div style={{ 
        margin: '20px 0', 
        padding: '24px', 
        border: '2px solid #e5e7eb', 
        borderRadius: '12px',
        backgroundColor: '#f9fafb'
      }}>
        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>📄 {fileName}</h3>
        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', marginBottom: '16px' }}>
          ¥{price}
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          <button 
            onClick={() => handlePayment('微信')}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              background: '#07c160',
              color: 'white'
            }}
          >
            💳 微信支付
          </button>
          <button 
            onClick={() => handlePayment('支付宝')}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              background: '#1677ff',
              color: 'white'
            }}
          >
            💳 支付宝
          </button>
          <button 
            onClick={() => setShowPayment(false)}
            style={{
              padding: '10px 20px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              background: 'white',
              color: '#6b7280'
            }}
          >
            🔙 返回
          </button>
        </div>
        <div style={{ marginTop: '12px', fontSize: '14px', color: '#6b7280' }}>
          ⚡ 支付完成后即可下载文件
        </div>
      </div>
    );
  }

  return (
    <div style={{ margin: '20px 0' }}>
      <button 
        onClick={handleDownload} 
        disabled={loading}
        style={{
          padding: '12px 24px',
          border: 'none',
          borderRadius: '8px',
          fontSize: '16px',
          fontWeight: '600',
          cursor: loading ? 'not-allowed' : 'pointer',
          background: isPaid ? '#3b82f6' : '#e5e7eb',
          color: isPaid ? 'white' : '#9ca3af',
          transition: 'all 0.3s ease'
        }}
      >
        {loading ? '⏳ 下载中...' : isPaid ? '📥 下载文件' : `🔒 付费解锁 ¥${price}`}
      </button>
      {error && <div style={{ marginTop: '8px', color: '#ef4444', fontSize: '14px', fontWeight: 'bold' }}>❌ {error}</div>}
    </div>
  );
}
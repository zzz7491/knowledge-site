import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';

export default function Admin() {
  const [files, setFiles] = useState([]);
  const [metadata, setMetadata] = useState({});
  const [loading, setLoading] = useState(true);
  const [password, setPassword] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deleting, setDeleting] = useState(null);
  const [editing, setEditing] = useState(null);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'admin123') {
      setAuthenticated(true);
    } else {
      alert('密码错误');
    }
  };

  const loadFiles = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/admin/list-files', {
        headers: { 'Authorization': 'Bearer admin-token-456' }
      });
      if (response.ok) {
        const data = await response.json();
        setFiles(data.files || []);
      }

      const metaResponse = await fetch('/api/admin/metadata', {
        headers: { 'Authorization': 'Bearer admin-token-456' }
      });
      if (metaResponse.ok) {
        const metaData = await metaResponse.json();
        const metaMap = {};
        metaData.files.forEach(item => {
          metaMap[item.key] = { price: item.price, hidden: item.hidden };
        });
        setMetadata(metaMap);
      }
    } catch (error) {
      console.error('加载失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/admin/upload', {
        method: 'POST',
        headers: { 'Authorization': 'Bearer admin-token-456' },
        body: formData
      });
      if (response.ok) {
        alert('上传成功！');
        loadFiles();
      } else {
        alert('上传失败');
      }
    } catch (error) {
      console.error('上传错误:', error);
      alert('上传出错');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (fileKey) => {
    if (!confirm(`确定删除 "${fileKey}" 吗？`)) return;
    setDeleting(fileKey);
    try {
      const response = await fetch(`/api/admin/delete?file=${encodeURIComponent(fileKey)}`, {
        method: 'DELETE',
        headers: { 'Authorization': 'Bearer admin-token-456' }
      });
      if (response.ok) {
        alert('删除成功！');
        loadFiles();
      } else {
        alert('删除失败');
      }
    } catch (error) {
      console.error('删除错误:', error);
      alert('删除出错');
    } finally {
      setDeleting(null);
    }
  };

  const handleSaveMetadata = async (key, price, hidden) => {
    try {
      const response = await fetch('/api/admin/metadata', {
        method: 'POST',
        headers: {
          'Authorization': 'Bearer admin-token-456',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key, price: parseFloat(price), hidden })
      });
      if (response.ok) {
        alert('保存成功！');
        loadFiles();
        setEditing(null);
      } else {
        alert('保存失败');
      }
    } catch (error) {
      console.error('保存错误:', error);
      alert('保存出错');
    }
  };

  useEffect(() => {
    if (authenticated) {
      loadFiles();
    }
  }, [authenticated]);

  if (!authenticated) {
    return (
      <Layout title="管理后台">
        <div style={{ maxWidth: '400px', margin: '100px auto', padding: '20px' }}>
          <h2>🔐 管理后台登录</h2>
          <form onSubmit={handleLogin}>
            <input
              type="password"
              placeholder="请输入管理密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                marginBottom: '12px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                fontSize: '16px'
              }}
            />
            <button
              type="submit"
              style={{
                width: '100%',
                padding: '12px',
                background: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              登录
            </button>
          </form>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="管理后台">
      <div style={{ maxWidth: '1000px', margin: '40px auto', padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h1 style={{ margin: 0 }}>📁 文件管理</h1>
          <button
            onClick={loadFiles}
            style={{
              padding: '8px 16px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            🔄 刷新列表
          </button>
        </div>

        <div style={{
          padding: '24px',
          border: '2px dashed #d1d5db',
          borderRadius: '12px',
          marginBottom: '24px',
          textAlign: 'center',
          background: '#f9fafb'
        }}>
          <h3 style={{ margin: '0 0 12px 0' }}>📤 上传文件到 R2</h3>
          <input
            type="file"
            onChange={handleUpload}
            disabled={uploading}
            style={{ display: 'none' }}
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            style={{
              display: 'inline-block',
              padding: '12px 24px',
              background: '#07c160',
              color: 'white',
              borderRadius: '8px',
              cursor: uploading ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              opacity: uploading ? 0.6 : 1
            }}
          >
            {uploading ? '⏳ 上传中...' : '📎 选择文件上传'}
          </label>
          <p style={{ fontSize: '14px', color: '#6b7280', marginTop: '8px' }}>
            支持所有文件类型，最大 100MB
          </p>
        </div>

        <div>
          <h3>📋 文件列表 ({files.length})</h3>
          {loading ? (
            <p>加载中...</p>
          ) : files.length === 0 ? (
            <p style={{ color: '#6b7280' }}>暂无文件</p>
          ) : (
            <div style={{ display: 'grid', gap: '8px' }}>
              {files.map((file) => {
                const meta = metadata[file.key] || { price: 0, hidden: 0 };
                const isEditing = editing === file.key;
                return (
                  <div
                    key={file.key}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '12px 16px',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      background: meta.hidden ? '#fef2f2' : 'white'
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: '500' }}>{file.key}</span>
                        {meta.hidden === 1 && (
                          <span style={{
                            background: '#ef4444',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '12px'
                          }}>隐藏</span>
                        )}
                        <span style={{ fontSize: '12px', color: '#6b7280' }}>
                          {(file.size / 1024).toFixed(2)} KB
                        </span>
                      </div>
                      {isEditing ? (
                        <div style={{ marginTop: '8px', display: 'flex', gap: '8px', alignItems: 'center' }}>
                          <input
                            type="number"
                            step="0.01"
                            defaultValue={meta.price}
                            id={`price-${file.key}`}
                            style={{
                              padding: '4px 8px',
                              borderRadius: '4px',
                              border: '1px solid #d1d5db',
                              width: '100px'
                            }}
                            placeholder="价格"
                          />
                          <label style={{ fontSize: '14px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <input
                              type="checkbox"
                              defaultChecked={meta.hidden === 1}
                              id={`hidden-${file.key}`}
                            />
                            隐藏文件
                          </label>
                          <button
                            onClick={() => {
                              const price = document.getElementById(`price-${file.key}`).value;
                              const hidden = document.getElementById(`hidden-${file.key}`).checked ? 1 : 0;
                              handleSaveMetadata(file.key, price, hidden);
                            }}
                            style={{
                              padding: '4px 12px',
                              background: '#07c160',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            💾 保存
                          </button>
                          <button
                            onClick={() => setEditing(null)}
                            style={{
                              padding: '4px 12px',
                              background: '#6b7280',
                              color: 'white',
                              border: 'none',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            取消
                          </button>
                        </div>
                      ) : (
                        <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '4px' }}>
                          价格: ¥{meta.price} | 状态: {meta.hidden ? '已隐藏' : '公开'}
                        </div>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      {!isEditing && (
                        <button
                          onClick={() => setEditing(file.key)}
                          style={{
                            padding: '4px 12px',
                            background: '#f59e0b',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          ⚙️ 设置
                        </button>
                      )}
                      <button
                        onClick={() => window.open(`/api/download?file=${encodeURIComponent(file.key)}`, '_blank')}
                        style={{
                          padding: '4px 12px',
                          background: '#3b82f6',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        📥 下载
                      </button>
                      <button
                        onClick={() => handleDelete(file.key)}
                        disabled={deleting === file.key}
                        style={{
                          padding: '4px 12px',
                          background: '#ef4444',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: deleting === file.key ? 'not-allowed' : 'pointer',
                          fontSize: '12px',
                          opacity: deleting === file.key ? 0.6 : 1
                        }}
                      >
                        {deleting === file.key ? '删除中...' : '🗑️ 删除'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
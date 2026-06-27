export async function onRequest(context) {
  const { request, env } = context;
  
  if (request.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const { email, password } = await request.json();
    
    if (!email || !password) {
      return new Response(JSON.stringify({ error: '邮箱和密码不能为空' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 简单密码哈希（生产环境建议用 bcrypt）
    const passwordHash = await hashPassword(password);

    const result = await env.knowledge_metadata.prepare(
      'INSERT INTO users (email, password_hash) VALUES (?, ?)'
    ).bind(email, passwordHash).run();

    return new Response(JSON.stringify({ 
      success: true, 
      message: '注册成功',
      userId: result.meta?.last_row_id 
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    if (error.message?.includes('UNIQUE constraint')) {
      return new Response(JSON.stringify({ error: '该邮箱已注册' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// 简单的哈希函数（生产环境请使用 bcrypt）
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password + 'secret-salt-123');
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}
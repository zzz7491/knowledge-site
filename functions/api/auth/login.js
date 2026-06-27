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

    const passwordHash = await hashPassword(password);

    const result = await env.knowledge_metadata.prepare(
      'SELECT id, email FROM users WHERE email = ? AND password_hash = ?'
    ).bind(email, passwordHash).first();

    if (!result) {
      return new Response(JSON.stringify({ error: '邮箱或密码错误' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 生成简易 JWT（生产环境请使用正式 JWT 库）
    const token = await generateJWT(result.id, result.email);

    return new Response(JSON.stringify({ 
      success: true, 
      token,
      user: { id: result.id, email: result.email }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password + 'secret-salt-123');
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function generateJWT(userId, email) {
  const header = { alg: 'HS256', typ: 'JWT' };
  const payload = { userId, email, exp: Math.floor(Date.now() / 1000) + 86400 };
  
  const encode = (obj) => {
    return btoa(JSON.stringify(obj)).replace(/=/g, '').replace(/\+/g, '-').replace(/\//g, '_');
  };
  
  const headerEncoded = encode(header);
  const payloadEncoded = encode(payload);
  const signature = await hashPassword(`${headerEncoded}.${payloadEncoded}`);
  
  return `${headerEncoded}.${payloadEncoded}.${signature}`;
}
export async function onRequest(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const fileKey = decodeURIComponent(url.searchParams.get('file') || '');
  
  if (!fileKey) {
    return new Response(JSON.stringify({ error: '缺少 file 参数' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // 解析 JWT Token
  const authHeader = request.headers.get('Authorization');
  let userId = null;
  let userEmail = null;
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7);
    const payload = await verifyJWT(token);
    if (payload) {
      userId = payload.userId;
      userEmail = payload.email;
    }
  }

  // 如果没有登录，尝试使用 demo token（向后兼容）
  if (!userId && authHeader === 'Bearer demo-token-123') {
    userId = 'demo';
    userEmail = 'demo@example.com';
  }

  // 检查文件元数据（价格和隐藏状态）
  const meta = await env.knowledge_metadata.prepare(
    'SELECT price, hidden FROM files WHERE key = ?'
  ).bind(fileKey).first();

  // 如果文件被隐藏，只有管理员可以访问
  if (meta && meta.hidden === 1) {
    const isAdmin = authHeader === 'Bearer admin-token-456';
    if (!isAdmin) {
      return new Response(JSON.stringify({ error: '文件已隐藏' }), {
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // 检查用户是否已购买（简单实现：检查用户订单表）
  if (meta && meta.price > 0 && userId && userId !== 'demo') {
    const order = await env.knowledge_metadata.prepare(
      'SELECT id FROM orders WHERE user_id = ? AND file_key = ? AND status = "paid"'
    ).bind(userId, fileKey).first();
    
    if (!order && !(authHeader === 'Bearer admin-token-456')) {
      return new Response(JSON.stringify({ 
        error: '请先付费购买',
        price: meta.price 
      }), {
        status: 402,
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }

  // 如果用户未登录，返回价格信息
  if (!userId && meta && meta.price > 0) {
    return new Response(JSON.stringify({ 
      error: '请先登录',
      price: meta.price 
    }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const object = await env.MY_R2_BUCKET.get(fileKey);
    if (!object) {
      return new Response(JSON.stringify({ error: '文件不存在' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const headers = new Headers();
    headers.set('Content-Type', object.httpMetadata?.contentType || 'application/octet-stream');
    const fileName = encodeURIComponent(fileKey.split('/').pop() || 'download');
    headers.set('Content-Disposition', `attachment; filename*=UTF-8''${fileName}`);
    
    return new Response(object.body, {
      headers: headers
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// JWT 验证函数
async function verifyJWT(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    
    const payload = JSON.parse(atob(parts[1]));
    if (payload.exp && payload.exp < Math.floor(Date.now() / 1000)) {
      return null; // Token 过期
    }
    
    return payload;
  } catch {
    return null;
  }
}
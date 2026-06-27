export async function onRequest(context) {
  const { request, env } = context;
  const authToken = request.headers.get('Authorization');
  
  if (authToken !== 'Bearer admin-token-456') {
    return new Response(JSON.stringify({ error: '未授权' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const url = new URL(request.url);
  const method = request.method;

  try {
    // GET: 获取所有文件的元数据
    if (method === 'GET') {
      const result = await env.knowledge_metadata.prepare(
        'SELECT * FROM files ORDER BY created_at DESC'
      ).all();
      
      return new Response(JSON.stringify({ files: result.results }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // POST: 设置文件价格和隐藏状态
    if (method === 'POST') {
      const body = await request.json();
      const { key, price, hidden } = body;
      
      if (!key) {
        return new Response(JSON.stringify({ error: '缺少 key 参数' }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' }
        });
      }

      await env.knowledge_metadata.prepare(
        `INSERT INTO files (key, price, hidden) 
         VALUES (?, ?, ?) 
         ON CONFLICT(key) DO UPDATE SET 
         price = excluded.price, 
         hidden = excluded.hidden`
      ).bind(key, price || 0, hidden ? 1 : 0).run();

      return new Response(JSON.stringify({ success: true, key, price, hidden }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response(JSON.stringify({ error: 'Method not allowed' }), {
      status: 405,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
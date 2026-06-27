export async function onRequest(context) {
  const { request, env } = context;
  const authToken = request.headers.get('Authorization');
  
  if (authToken !== 'Bearer admin-token-456') {
    return new Response(JSON.stringify({ error: '未授权' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  try {
    const url = new URL(request.url);
    const fileKey = decodeURIComponent(url.searchParams.get('file') || '');
    
    if (!fileKey) {
      return new Response(JSON.stringify({ error: '缺少 file 参数' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    await env.MY_R2_BUCKET.delete(fileKey);

    return new Response(JSON.stringify({ 
      success: true, 
      key: fileKey 
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
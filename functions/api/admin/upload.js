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
    const formData = await request.formData();
    const file = formData.get('file');
    
    if (!file) {
      return new Response(JSON.stringify({ error: '未上传文件' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const fileName = file.name;
    const fileBuffer = await file.arrayBuffer();
    
    await env.MY_R2_BUCKET.put(fileName, fileBuffer, {
      httpMetadata: {
        contentType: file.type || 'application/octet-stream'
      }
    });

    return new Response(JSON.stringify({ 
      success: true, 
      key: fileName,
      size: file.size 
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
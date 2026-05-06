import {useState} from 'react';import {uploadDrawing,getModelUrl} from './api/api';
export default function App(){const [f,setF]=useState(); const [url,setUrl]=useState(''); const [status,setStatus]=useState('idle');
const run=async()=>{if(!f)return;setStatus('processing');const r=await uploadDrawing(f);setUrl(getModelUrl(r.job_id));setStatus(r.status)}
return <div><h1>CV3D</h1><input type='file' accept='image/*' onChange={e=>setF(e.target.files?.[0])}/><button onClick={run}>Convert to 3D Model</button><div>{status}</div>{url&&<a href={url}>Download GLB</a>}</div>}

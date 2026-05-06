import axios from 'axios'
export const uploadDrawing=async(file)=>{const fd=new FormData();fd.append('drawing',file);return (await axios.post('/api/reconstruct',fd)).data}
export const getJob=async(id)=>(await axios.get(`/api/jobs/${id}`)).data
export const getModelUrl=(id)=>`/api/jobs/${id}/model.glb`
export const checkHealth=async()=>(await axios.get('/api/health')).data

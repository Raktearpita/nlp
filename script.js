async function checkSpam(){
  let msg = document.getElementById('msgInput').value;
  if(!msg) return alert("Message likh!");
  let resDiv = document.getElementById('result');
  resDiv.style.display='block';
  resDiv.innerHTML='⏳ Checking with 97.04% model...';
  resDiv.className='';
  
  let response = await fetch('/predict', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message: msg})
  });
  let data = await response.json();
  
  if(data.prediction=='spam'){
    resDiv.className='spam';
    resDiv.innerHTML=`🚨 SPAM - ${data.confidence}% sure | Accuracy 97.04%`;
  } else {
    resDiv.className='ham';
    resDiv.innerHTML=`✅ HAM - ${data.confidence}% sure | Accuracy 97.04%`;
  }
}
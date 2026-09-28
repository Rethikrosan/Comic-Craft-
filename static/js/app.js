const form=document.getElementById("comic-form");
const button=document.getElementById("generate-btn");
if(form&&button){form.addEventListener("submit",()=>{button.disabled=true;button.textContent="Creating your comic…";});}

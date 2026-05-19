
const api="http://127.0.0.1:8000"

async function loadUsers(){
let res=await fetch(api+"/users")
let data=await res.json()

let table=document.getElementById("usersTable")
if(!table)return

table.innerHTML=""

data.forEach(user=>{
table.innerHTML+=`
<tr>
<td>${user.id}</td>
<td>${user.username}</td>
<td>${user.email}</td>
<td><button onclick="deleteUser(${user.id})">Delete</button></td>
</tr>
`
})

let count=document.getElementById("usersCount")
if(count)count.innerText=data.length
}

async function addUser(){
let username=document.getElementById("username").value
let email=document.getElementById("email").value

await fetch(api+"/users",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({username:username,email:email})
})

loadUsers()
}

async function deleteUser(id){
await fetch(api+"/users/"+id,{method:"DELETE"})
loadUsers()
}

async function loadProjects(){
let res=await fetch(api+"/projects")
let data=await res.json()

let table=document.getElementById("projectsTable")
if(!table)return

table.innerHTML=""

data.forEach(project=>{
table.innerHTML+=`
<tr>
<td>${project.id}</td>
<td>${project.name}</td>
<td><button onclick="deleteProject(${project.id})">Delete</button></td>
</tr>
`
})

let count=document.getElementById("projectsCount")
if(count)count.innerText=data.length
}

async function addProject(){
let name=document.getElementById("projectName").value

await fetch(api+"/projects",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({name:name})
})

loadProjects()
}

async function deleteProject(id){
await fetch(api+"/projects/"+id,{method:"DELETE"})
loadProjects()
}

loadUsers()
loadProjects()

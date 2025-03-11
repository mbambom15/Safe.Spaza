document.getElementById("CustomerRedirect").addEventlistener("click",function(){
	window.location.href = "customer_page.html";
});

document.getElementById("loginForm").addEventlistener("submit",function(event)
	event.preventDefault();

	let userType = document.querySelector('input[name = "userType"]: checked')

		if(!userType){
			alert("Please select a user type");
			return;
		}

	  if(userType.value === "manufacturer"){
	  	window.location.href = "manufacturer.html";
	  }else if(userType.value ==="spaza-owner"){
	  	window.location.href = "spaza-owner.html"
	  }

	});
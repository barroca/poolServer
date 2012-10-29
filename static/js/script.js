var selected = 0; 
function checkform(theform){
	var why = "";
	 
	if(theform.recaptcha_response_field.value == ""){
		why += "Por favor preencha as palavras para validar o voto.\n";
	}
	if(selected == 0){
		why += "- Por favor escolha 1 candidato.\n";
	}

	if(why != ""){
		alert(why);
		return false;
	}
}


function part1selected(){
	var p1  = document.getElementById('foto1');
	var p2  = document.getElementById('foto2');
	p1.style.borderColor='#ffa500'; 
	p2.style.borderColor='#dddddd'; 
	selected = 1;
	document.forms['form3'].elements['vote'].value = "1";
}

function part2selected(){
	var p1  = document.getElementById('foto1');
	var p2  = document.getElementById('foto2');
	p2.style.borderColor='#ffa500'; 
	p1.style.borderColor='#dddddd'; 
	selected = 2;
	document.forms['form3'].elements['vote'].value = "2";
}

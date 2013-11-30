var langs = ["en", "it"];

function getMenu(lang)
{
	var a = document.createElement("a");
	a.href = "javascript:void(0)";
	a.className = "item";
	a.appendChild(document.createTextNode(lang));
	document.getElementById("span").appendChild(a);
	
	a.onclick = function(){
		var div = document.createElement("div");
		div.style.backgroundColor = "rgba(0,0,0,0.0)";
		div.style.position = "fixed";
		div.style.top = 0;
		div.style.left = 0;
		div.style.textAlign = "center";
		div.style.width = "100%";
		div.style.height = document.documentElement.clientHeight+"px";
		div.onclick = function(){document.body.removeChild(div)};
		var menu = document.createElement("div");
		menu.style.backgroundColor = "rgb(0,0,0)";
		menu.style.position = "fixed";
		menu.style.top = document.getElementById("nav_menu").getBoundingClientRect().bottom+"px";
		menu.style.left = a.getBoundingClientRect().left+"px";
		for (var i=0; i<langs.length; i++)
		{
			if (lang != langs[i])
			{
				var item = document.createElement("a");
				item.className = "item";
				item.href = "../"+langs[i]+"/index.html";
				item.appendChild(document.createTextNode(langs[i]));
				menu.appendChild(item);
			}
		}
		div.appendChild(menu);
		document.body.appendChild(div);
		menu.style.left = document.documentElement.clientWidth - menu.getBoundingClientRect().width+"px";
	}
}

function clickOnImage(img)
{
	var div = document.createElement("div");
	div.style.backgroundColor = "rgba(0,0,0,0.8)";
	div.style.position = "fixed";
	div.style.top = 0;
	div.style.left = 0;
	div.style.textAlign = "center";
	div.style.width = "100%";
	div.style.height = document.documentElement.clientHeight+"px";
	div.onclick = function(){document.body.removeChild(div)};
	newImg = document.createElement("img");
	newImg.setAttribute("src", img.getAttribute("src"));
	newImg.onclick = function(event){
		var imgs = document.getElementsByClassName("screen");
		var i = 0;
		while (imgs[i].src != newImg.src) {i++;}
		i++;
		if (i < imgs.length) {newImg.src = imgs[i].src;}
		else {document.body.removeChild(div)}
		event.stopPropagation();
		};
	var w = newImg.width,
	h = newImg.height,
	wRatio = 1,
	hRatio = 1;
	if (w > document.documentElement.clientWidth)
	{
		wRatio = document.documentElement.clientWidth/w;
	}
	if (h > document.documentElement.clientHeight)
	{
		hRatio = document.documentElement.clientHeight/h;
	}
	var ratio = wRatio < hRatio ? wRatio : hRatio;
	newImg.width = Math.ceil(w*ratio);
	newImg.height = Math.ceil(h*ratio);
	div.appendChild(newImg);
	document.body.appendChild(div);
}
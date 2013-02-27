
//popup flag - 0 means disabled, 1 means enabled
var popupStatus = 0;
//ajax(segmenting) flag - 0 means disabled, 1 means enabled
var ajaxRequest = 0;


function showPopup(){
	if(popupStatus==0){
		$("#popupBkg").css({
			"opacity": "0.7"
		});
		$("#popupBkg").fadeIn("slow");
		$("#popup").fadeIn("slow");
		popupStatus = 1;
	}
}

function hidePopup(){	
	if(popupStatus==1){
		$("#popupBkg").fadeOut("slow");
		$("#popup").fadeOut("slow");
		popupStatus = 0;
	}
}

function centerPopup(){
	//request data for centering
	var windowWidth = document.documentElement.clientWidth;
	var windowHeight = document.documentElement.clientHeight;
	var popupHeight = $("#popup").height();
	var popupWidth = $("#popup").width();
	//centering
	$("#popup").css({
		"position": "absolute",
		"top": windowHeight/2-popupHeight/2,
		"left": windowWidth/2-popupWidth/2
	});
	//only need force for IE6	
	$("#popupBkg").css({
		"height": windowHeight
	});
}

function clearDepictErr(){
	$("#depictErr").text("");
	$("#depictErr").hide();
}
function clearTagErr(){
	$("#tagErr").text("");
	$("#tagErr").hide();
}

function clearPopup(){
	//clear errors
	clearDepictErr();
	clearTagErr();
	//clear tags
	$("#genTags").empty();
	$("#tagAreas").hide();
	//clear textarea
	$("#inDepict").val("");
	$("#pHint").show();
	$("#inputArea").show();
	//clear static text
	$("#depict").text("");
	$("#depict").hide();
	//hide loading
	$("#segmenting").hide();
	//enable ok button
	enableBtn($("#depictOk"));
	//show ok button
	$("#depictOk").parent("span").show();
	//hide revise link
	$("#reDepict").parent("span").hide();
	//hide form submit
	$("#popupCon").find(".formAct").hide();
}

function initPopup(scn){
	//clear
	clearPopup();
	
	if(scn == "1")
	{
		$("#popupTitle").text("Marketing to own fans");
		$("#formOk").val("Generate target fans");
		$("#scnForm").attr("action", "own_fans_filter");  //!!!
	}
	else if(scn == "2")
	{
		$("#popupTitle").text("Realtime marketing to the whole sina weibo network");
		$("#formOk").val("Generate target users");
		$("#scnForm").attr("action", "realtime_keyword_matching");  //!!!
	}
	else if(scn == "3")
	{
		$("#popupTitle").text("Marketing based on similar hot weibo");
		$("#formOk").val("Generate target users");
		$("#scnForm").attr("action", "近似热门微博关键节点营销.html");  //!!!
	}
	
	centerPopup();
	showPopup();
}

function closePopup(){
	hidePopup();	
	//reset ajax flag
	ajaxRequest = 0;
}


function tagClickEvt(){
	if($(this).hasClass("clicked"))
	{
		$(this).removeClass("clicked");
	}
	else
	{
		$(this).addClass("clicked");
	}
}

function highlightBtnEvt(){
	$(this).addClass("hover");
}
function unhighlightBtnEvt(){
	$(this).removeClass("hover");
}
function disableBtn(btnInput){
	btnInput.removeClass("hover");
	btnInput.attr("disabled", "disabled");
	btnInput.unbind("mouseenter");
	btnInput.unbind("mouseleave");
}
function enableBtn(btnInput){
	btnInput.removeAttr("disabled");
	btnInput.mouseenter(highlightBtnEvt);
	btnInput.mouseleave(unhighlightBtnEvt);
}



$(document).ready(function(){

	//========================================
	//event binding for selection highlight
	//========================================
	$(".scnItem").mouseenter(function(){
		$(this).addClass("current");
	});
	
	$(".scnItem").mouseleave(function(){
		$(this).removeClass("current");
	});
	
	$("#inDepict").focus(function(){
		$("#inputArea").addClass("clicked");
	});
	
	$("#inDepict").blur(function(){
		$("#inputArea").removeClass("clicked");
	});
	
	$(".btn-flat").find("input").mouseenter(highlightBtnEvt);	
	$(".btn-flat").find("input").mouseleave(unhighlightBtnEvt);
	
	
	//=========================
	//event binding for pupup
	//=========================
	$(".scnItem").click(function(){		
		var scn = $(this).attr("data-scn");
		initPopup(scn);
	});

	$("#popupClz").click(function(){
		closePopup();
	});	
	
	
	//===================================
	//event binding for buttons in popup
	//===================================
	$("#depictOk").click(function(){
		
		var depict = ($("#inDepict").val()).trim();
		//length validation
		if(depict.length > 0)
		{
			clearDepictErr();
			
			//hide textarea
			$("#pHint").hide();
			$("#inputArea").hide();
			//show loading
			$("#segmenting").show();
			//disable ok button
			disableBtn($("#depictOk"));
			
			//set ajax flag
			ajaxRequest = 1;
			//ajax call......  //!!!
			 $.get("cut",  { depict: depict},  function(result){  
				//show static text
				$("#depict").text(depict);
				$("#depict").show();
				//hide loading
				$("#segmenting").hide();
				if (result.error) {
					
				}
				else {
				   //generate tags			
					var tagsCode = "";
					var result=eval("("+result+")");
					for(var i in result.goods)
					{
						tagsCode += "<a class=\"tag clicked\" data-name=\"" + result.goods[i] + "\">" + result.goods[i] + "</a>";
					}
					
					for(var i in result.noun)
					{
						tagsCode += "<a class=\"tag\" data-name=\"" + result.noun[i] + "\">" + result.noun[i] + "</a>";
					}
					for(var i in result.adj)
					{
						tagsCode += "<a class=\"tag\" data-name=\"" + result.adj[i] + "\">" + result.adj[i] + "</a>";
					}
					
					$("#genTags").html(tagsCode);
					//bind event on tags
					$(".tag").click(tagClickEvt);			
					
					//enable ok button
					enableBtn($("#depictOk"));
					//hide ok button
					$("#depictOk").parent("span").hide();
					//show revise link
					$("#reDepict").parent("span").show();
					//show tag area
					$("#tagAreas").slideDown("fast", centerPopup);
					//show form submit
					$("#popupCon").find(".formAct").show();
				}
				}   
			);  
		}
		else
		{
			$("#depictErr").text("Depict can't be null");
			$("#depictErr").show();
		}
		
	});
	
	
	$("#reDepict").click(function(){
		//show textarea
		$("#pHint").show();
		$("#inputArea").show();
		$("#inDepict").focus();
		//hide static text
		$("#depict").hide();
		
		//show ok button
		$("#depictOk").parent("span").show();
		//hide revise link
		$("#reDepict").parent("span").hide();
		//hide tag area
		$("#tagAreas").slideUp("fast", centerPopup);
		//hide form submit
		$("#popupCon").find(".formAct").hide();
	});
	
	
	$("#formOk").click(function(){
		var tags = new Array();
		$(".tag.clicked").each(function(){
			tags.push($(this).attr("data-name"));
		});
		
		var inputTags = ($("#inTags").val()).trim();
		if(inputTags.length > 0)
		{
			var temps = inputTags.split(" ");  //空格分割
			for(var i in temps)
			{
				if(temps[i].length > 0)
				{
					//if the tag already exists
					var depulicated = false;
					for(var j in tags)
					{
						if(tags[j] == temps[i])
						{
							depulicated = true;
							break;
						}
					}
					
					if(depulicated == false)
					{
						tags.push(temps[i]);
					}
				}
			}
		}
		
		//alert(tags);
		if(tags.length > 0)
		{
			clearTagErr();
			
			//把tags传到下一个页面
			alert("Selected tags：" + tags);  //!!!
			$("#scnForm").find("input[name='tags']").val(tags);
			$("#scnForm").submit();
		}
		else
		{
			$("#tagErr").text("Make sure at least one tag should be selected");
			$("#tagErr").show();
		}
		
	});

	
});

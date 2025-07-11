document.addEventListener('DOMContentLoaded', function() {
    $('body').find('[contenteditable]').removeAttr('contenteditable');
});

var input = document.getElementById("search");

//Execute a function when the user releases a key on the keyboard
input.addEventListener("keyup", function(event) {
// Number 13 is the "Enter" key on the keyboard
if (event.keyCode === 13) {
 // Cancel the default action, if needed
 event.preventDefault();
 // Trigger the button element with a click
 document.getElementById("submit").click();
}
});

$(function(){var a=$(".col-md-2 .sidebar");320>=window.innerWidth&&($("body").css("fontSize","95%"),$("button").css("fontSize","85%"));/iPhone|iPod|iPad/i.test(navigator.userAgent)&&$(".btn-quick-guide").css("display","none");$("#pull").unbind("click").on("click",function(d){d.preventDefault();d.stopPropagation();window.scrollTo(0,0);a.toggle("slide")})});
(function(a){a.extend({scrollToTop:function(){var d=!1;a("body").append(a("<a />").addClass("scroll-to-top").attr({href:"#",id:"scrollToTop"}).append(a("<i />").addClass("icon icon-chevron-up icon-white")));a("#scrollToTop").click(function(d){d.preventDefault();a("body, html").animate({scrollTop:0},500);return!1});a(window).scroll(function(){var b=a(window).scrollTop();35>b?a("#pull").attr("style","top: 24px!important"):35<b&&(b-=10,a("#pull").attr("style","top: "+b+"px!important"));d||(d=!0,150<
a(window).scrollTop()?a("#scrollToTop").stop(!0,!0).addClass("visible"):a("#scrollToTop").stop(!0,!0).removeClass("visible"),d=!1)})}})})(jQuery);
(function(a){var d={action:function(){},runOnLoad:!1,duration:500},b=!1,f,c={init:function(){for(var b=0;b<=arguments.length;b++){var l=arguments[b];switch(typeof l){case "function":d.action=l;break;case "boolean":d.runOnLoad=l;break;case "number":d.duration=l}}return this.each(function(){d.runOnLoad&&d.action();a(this).resize(function(){c.timedAction.call(this)})})},timedAction:function(a,c){var m=function(){var a=d.duration;if(b&&(a=d.duration-(new Date-f),0>=a)){clearTimeout(b);b=!1;d.action();
return}b=setTimeout(m,a)};f=new Date;"number"===typeof c&&(d.duration=c);"function"===typeof a&&(d.action=a);b||m()}};a.fn.afterResize=function(a){return c[a]?c[a].apply(this,Array.prototype.slice.call(arguments,1)):c.init.apply(this,arguments)}})(jQuery);
(function(){var a={initialized:!1,initialize:function(){this.initialized||(this.initialized=!0,this.build(),this.events())},build:function(){$.scrollToTop();this.featuredBoxes();this.toggle()},events:function(){$(window).afterResize(function(){a.featuredBoxes();a.checkStickyMenu()})},stickyMenu:function(){if($("body").hasClass("boxed"))return!1;var a=$("body header:first"),b=a.height(),f=a.find(".logo"),c=a.find(".logo img"),k=c.width(),l=c.height(),m=this;c.css("height",40);var g=c.width();c.css("height",
"auto").css("width","auto");var e=$("header.flat-menu ul.nav-main > li > a");m.checkStickyMenu=function(){if($("body").hasClass("boxed"))return!1;if($(window).scrollTop()>b-15-40&&991<$(window).width()){if($("body").hasClass("sticky-menu-active"))return!1;c.stop(!0,!0);$("body").addClass("sticky-menu-active").css("padding-top",b);e.addClass("sticky-menu-active");f.addClass("logo-sticky-active");c.animate({width:g,height:40,top:"28px"},200,function(){})}else $("body").hasClass("sticky-menu-active")&&
($("body").removeClass("sticky-menu-active").css("padding-top",0),e.removeClass("sticky-menu-active"),f.removeClass("logo-sticky-active"),c.animate({width:k,height:l,top:"0px"},200,function(){c.css({width:"auto",height:"auto"})}))};$(window).on("scroll",function(){m.checkStickyMenu()});m.checkStickyMenu()},featuredBoxes:function(){$("div.featured-box").css("height","auto");$("div.featured-boxes").each(function(){var a=$(this),b=0;$("div.featured-box",a).each(function(){$(this).height()>b&&(b=$(this).height())});
$("div.featured-box",a).height(b)})},toggle:function(){$("section.toggle > label").prepend($("<i />").addClass("icon icon-plus"));$("section.toggle > label").prepend($("<i />").addClass("icon icon-minus"));$("section.toggle.active > p").addClass("preview-active");$("section.toggle.active > div.toggle-content").slideDown(350,function(){});$("section.toggle > label").click(function(a){var b=$(this).parent(),f=$(this).parents("div.toogle"),c=!1;f.hasClass("toogle-accordion")&&"undefined"!=typeof a.originalEvent&&
f.find("section.toggle.active > label").trigger("click");b.toggleClass("active");if(b.find("> p").get(0)){c=b.find("> p");a=c.css("height");c.css("height","auto");var k=c.css("height");c.css("height",a)}a=b.find("> div.toggle-content");b.hasClass("active")?($(c).animate({height:k},350,function(){$(this).addClass("preview-active")}),a.slideDown(350,function(){})):($(c).animate({height:25},350,function(){$(this).removeClass("preview-active")}),a.slideUp(350,function(){}))})}};a.initialize();$(window).load(function(){a.stickyMenu()})})();
(function(a){a.TryIt=function(d,b){var f={url:d},c=this;c.settings={};c.compile=function(){a(".prettyprint.tryit").click(function(b){var d=a(this).text(),g="",e="",f="",k="",n="";if(a(this).attr("title")){var h=a(this).attr("title").split(",");h[0]&&(g=a("#"+h[0].trim()+"").text());h[1]&&(e=a("#"+h[1].trim()+"").text());h[2]&&(n=h[2],f=a("#"+h[2].trim()+"").text());h[3]&&(n=h[3],k=a("#"+h[3].trim()+"").text())}a("#source").text(d);a("#supportsource").text(g);a("#utilsource").text(e);a("#extrasource").text(f);
a("#inputs").text(k);a("#filename").text(n);d=a(this).width()+12;a(this).height();g=a(this).offset().left;e=a(this).offset().top;g=Math.round(g);g=b.pageX-g;X=d-g;e=Math.round(e);e=b.pageY-e;36>=X&&36>=e&&(b.preventDefault(),768>=window.innerWidth?(b=window.innerHeight,a.colorbox({iframe:!0,reposition:!0,opacity:.35,href:c.settings.url,width:window.innerWidth,height:b})):(a(window).height(),a.colorbox({iframe:!0,reposition:!0,opacity:.35,href:c.settings.url,width:960,height:650})))})};var k=a(window).innerWidth()/
2-320;a(".inline").colorbox({inline:!0,left:k,width:"615px",opacity:.5});(function(){c.settings=a.extend({},f,b);a("body").append('<div id="source" style="display:none;"></div>');a("body").append('<div id="supportsource" style="display:none;"></div>');a("body").append('<div id="utilsource" style="display:none;"></div>');a("body").append('<div id="extrasource" style="display:none;"></div>');a("body").append('<div id="inputs" style="display:none;"></div>');a("body").append('<div id="filename" style="display:none;"></div>');
a(".prettyprint.tryit").mousemove(function(b){var c=a(this).width()+12;a(this).height();var d=a(this).offset().left,e=a(this).offset().top,d=Math.round(d),d=b.pageX-d;X=c-d;e=Math.round(e);e=b.pageY-e;36>=X&&36>=e?a(this).css("cursor","pointer"):a(this).css("cursor","default")})})()}})(jQuery);
$(document).ready(function(){
	var a=location.href;
	
	filename=a.substring(a.lastIndexOf(".com")+5);
	-1==filename.lastIndexOf(".jsp")&&(filename+="index.jsp");
	0==$('.sidebar li a[href*= "'+filename+'"]').text().length&&(filename=$(".parent-file").text());
	-1==filename.lastIndexOf("whoiswho")&&($('.sidebar li a[href*= "'+filename+'"]').css("color",""),$('.sidebar li a[href*= "'+filename+'"]').css("background-color","#FFA500").css("color","#FFFFFF"))
	
});
$(window).load(function(){$(".middle-col").height()<$(".sidebar").height()&&991<window.innerWidth&&$(".middle-col").css("height",$(".sidebar").height()+50);$(".middle-col").height()<$("#rightbar").height()&&991<window.innerWidth&&$(".middle-col").css("height","1192");/iPhone|iPad|iPod/i.test(navigator.userAgent)&&($("#android").hide(),$("#microsoft").hide(),$(".hide-me").hide())});function resizeFrame(a){a.height="0px";a.height=a.contentWindow.document.body.scrollHeight+5+"px"}
468>window.innerWidth&&($(".topgooglead").html(""),$(".topgooglead").html('<script async src="//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js">\x3c/script><ins class="adsbygoogle"     style="display:inline-block;width:300px;height:00px"     data-ad-client="ca-pub-2373417360267295"    data-ad-slot="5533741760"></ins><script>(adsbygoogle = window.adsbygoogle || []).push({});\x3c/script>'));




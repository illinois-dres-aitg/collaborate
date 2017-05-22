/*********************************
// Version 1.0
// last edited 12/2007 by Jon Gunderson
*********************************/


// Initialize global variables used to initial widgets and provide browser independence for handling events and lack of namespace support in IE DOM functions

var VIEW_PRINT  = 1;
var VIEW_SCREEN = 2;

var FONT_SIZE_XSMALL = 1;
var FONT_SIZE_SMALL  = 2;
var FONT_SIZE_MEDIUM = 3;
var FONT_SIZE_LARGE  = 4;
var FONT_SIZE_XLARGE = 5;

var document_font_size = documentGetFontSize();

function saveCookieData() {

  var cookie = "";
  cookie += "font-size=" + document_font_size;
  cookie += "; path=" + cookie_path;
  cookie += "; domain=" + cookie_domain; 
  cookie += "; max-age=" + (60*60*24*365);

  document.cookie = cookie;

}

function getCookieDataNumber( label_name, default_value ) {

  var label_length = label_name.length+1;
  var pos1;
  var pos2;
  var value = default_value;

  var cookie_data = document.cookie;
	
  pos1 = cookie_data.indexOf(label_name); 

  if( pos1 != -1 ) {

    pos1 = pos1 + label_length;

    pos2 = cookie_data.indexOf(";", pos1 );

    if( pos2 == -1 )
       pos2 = cookie_data.length

    value = decodeURIComponent(cookie_data.substring( pos1, pos2 ));

  } // endif

  value = Number( value );

  if( value.NaN )
    value = Number(default_value);

  return value;

}


function documentSetFontSize( size ) {

  document_font_size = size;

  saveCookieData();

}

function documentGetFontSize() {

  document_font_size = getCookieDataNumber( "font-size", FONT_SIZE_MEDIUM );

  return document_font_size;

}

/* 
 *
 * @params ( string ) title is the string associated with the TITLE attribute on the LINK elements to enable
 * 
 * @return none
 */

function setStylesheetByTitle(title) {
	
  var stylesheets = document.getElementsByTagName("link");
	
  for(var i=0; i < stylesheets.length; i++) {
		
    /* Added test link to make sure link has rel attribute and therefore a stylesheet */ 
    if( stylesheets[i].getAttribute("rel") && 
        stylesheets[i].getAttribute("rel").indexOf("style") != -1 && 
        stylesheets[i].getAttribute("title") 
      ) {
			
      // By default disable stylesheet
      stylesheets[i].disabled = true
      // Hack to disable alternative stylesheets for IE
      stylesheets[i].setAttribute("rel","alternative stylesheet");

      // Test if stylesheet should be enabled
      if(stylesheets[i].getAttribute("title") == title) {
        stylesheets[i].disabled = false; //enable chosen style sheet
			  // Hack for IE
			  stylesheets[i].setAttribute("rel","stylesheet");
			} // endif
			
    }  // endif
			
  }  // end for
	
}

function handleSetView( view ) {

  var node_print = document.getElementById("printst");
  var node_screen = document.getElementById("screenst");

  switch( view ) {

    case VIEW_PRINT:
         setStylesheetByTitle("print");
         node_print.style.display = "none";
         node_screen.style.display = "block";
         break;

    case VIEW_SCREEN:
    default: 
		     if( window.navigate ) {
					 // if IE just reload the page. its easier
					 window.navigate( window.location.href );
				 } else {
           setStylesheetByTitle("screen");
           node_print.style.display = "block";
           node_screen.style.display = "none";
				 }
         break;
		
  } // end switch
	
}


function handleSetFontSize( size ) {

  var node = document.getElementById('container');

  documentSetFontSize( size );

  // Remove selection 
  document.getElementById('sizexsmall').className = "";
  document.getElementById('sizesmall').className  = "";
  document.getElementById('sizemedium').className = "";
  document.getElementById('sizelarge').className  = "";
  document.getElementById('sizexlarge').className = "";
	
  switch( size ) {
		
    case FONT_SIZE_XSMALL:
         node.style.fontSize = "80%";
         document.getElementById('sizexsmall').className = "selected";
         break;

    case FONT_SIZE_SMALL:
         node.style.fontSize = "90%";
         document.getElementById('sizesmall').className = "selected";
         break;
		
    case FONT_SIZE_MEDIUM:
         node.style.fontSize = "100%";
         document.getElementById('sizemedium').className = "selected";
         break;
		
    case FONT_SIZE_LARGE:
         node.style.fontSize = "110%";
         document.getElementById('sizelarge').className = "selected";
         break;
		
    case FONT_SIZE_XLARGE:
         node.style.fontSize = "120%";		
         document.getElementById('sizexlarge').className = "selected";
         break;

    default:
         node.style.fontSize = "110%";
         document.getElementById('sizelarge').className = "selected";
         page_prefs.font_size = FONT_SIZE_MEDIUM;
         break;
  } // end switch
	
}

var widgets_flag = false;

function initCITA() {
	
  //
  handleSetFontSize( documentGetFontSize() );

  // Setup Menu
  var sidebar = new SidebarMenu("sidenav");
  sidebar.init();

// Round corners 
  roundCorners("header");
  roundCorners("toolbar");
  roundCorners("sidenav");
  roundCorners("pagenav");
  roundCorners("codebox");

  roundExamples();

  var node_container = document.getElementById("container");

  // show page while after everything is finished intializing
  if( node_container )
    node_container.style.visibility = "visible";	

  // Check to see if there are ARIA widgets on the page and initialize

  if( widgets_flag ) {
    initApp();
  } // endif

}


// ***********************
//
//
//
// **********************

function roundExamples() {

  var size = 4;

  // test if browser supports DOM methods

  if( !document.getElementsByClassName )
    return;

  // get node to round corners
  var node_targets = document.getElementsByClassName("examplebox");

  for(var i=0; i < node_targets.length; i++ ) {

    var color_parent = getBackgroundColor(node_targets[i].parentNode);
    var color_target = getBackgroundColor(node_targets[i]);
	var color_border = calcBorderColor(color_parent, color_target);
	var bkgrd_image  = getBackgroundImageURL(node_targets[i]);
	var bkgrd_repeat = getBackgroundImageRepeat(node_targets[i]);

    // set padding of target to 0px
    node_targets[i].style.padding = "0px";

    // Add SPAN markup for rounding corners
  
    // add markup for top
    var node_container = document.createElement("span");

    // add node to the DOM
    if( node_targets[i].firstChild ) {
      node_targets[i].insertBefore( node_container, node_targets[i].firstChild );
	  node_container = node_targets[i].firstChild;
	} else {
      node_targets[i].appendChild( node_container );
	  node_container = node_targets[i].lastChild;
	}  // endif
  
    node_container.className = "rounded";
    node_container.backgroundColor = color_parent;

    for(var j = 1; j <= size; j++ ) {
      var node_child = document.createElement("span");
      node_container.appendChild( node_child );
	  node_child = node_container.lastChild;
      node_child.className = "line" + i;
      node_child.style.backgroundImage = bkgrd_image;
      node_child.style.backgroundRepeat = bkgrd_repeat;
      node_child.style.backgroundColor = color_target;
      node_child.style.borderColor = color_border;
    }  // endfor

  } // endfor
  
}


// ***********************
//
//
//
// **********************

function roundCorners( id ) {

  var size = 4;

  // test if browser supports DOM methods

  if( !document.getElementById )
    return;

  // get node to round corners
  var node_target = document.getElementById( id );

  // test to see if node is in document
  if( !node_target ) 
   return;

  var color_parent = getBackgroundColor(node_target.parentNode);
  var color_target = getBackgroundColor(node_target);
	var color_border = calcBorderColor(color_parent, color_target);
	var bkgrd_image  = getBackgroundImageURL(node_target);
	var bkgrd_repeat = getBackgroundImageRepeat(node_target);

  // set padding of target to 0px
  node_target.style.padding = "0px";

  // Add SPAN markup for rounding corners
  
  // add markup for top
  var node_container = document.createElement("span");

  // add node to the DOM
  if( node_target.firstChild ) {
    node_target.insertBefore( node_container, node_target.firstChild );
		node_container = node_target.firstChild;
		
	} else {
    node_target.appendChild( node_container );
		node_container = node_target.lastChild;
	}
  
  node_container.className = "rounded";
  node_container.backgroundColor = color_parent;

  for(var i = 1; i <= size; i++ ) {
    var node_child = document.createElement("span");
    node_container.appendChild( node_child );
		node_child = node_container.lastChild;
    node_child.className = "line" + i;
    node_child.style.backgroundImage = bkgrd_image;
    node_child.style.backgroundRepeat = bkgrd_repeat;
    node_child.style.backgroundColor = color_target;
    node_child.style.borderColor = color_border;
  }

  // add markup for bottom

  var node_container = document.createElement("span");

  // add node to the DOM
  node_target.appendChild( node_container );

  node_container.className = "rounded";
  node_container.backgroundColor = color_parent;

  for(var i = size; i > 0; i-- ) {
    var node_child = document.createElement("span");
    node_child.className = "line" + i;
    node_container.appendChild( node_child );
    node_child.style.backgroundImage = bkgrd_image;
    node_child.style.backgroundRepeat = bkgrd_repeat;
    node_child.style.backgroundColor = color_target;
    node_child.style.borderColor = color_border;
  }

  
}

function getBackgroundColor( node ) {
  var color = getStyleProp(node,"backgroundColor");
	
  if( (color == null) || 
		  (color.indexOf("transparent") != -1 ) || 
		  (color.indexOf("rgba(0, 0, 0, 0)") != -1 ) 
		)
    return "transparent";
		
  if(color.indexOf("rgb") != -1 ) 
	  color=rgb2hex(color);
	
  return color ;
	
}

function getBackgroundImageURL( node ) {
  var image = getStyleProp(node,"backgroundImage");
	
	if( image == "none" )
	  image = "url()";
	
  return image;
	
}

function getBackgroundImageRepeat( node ) {
  var repeat = getStyleProp(node,"backgroundRepeat");
	
  return repeat;
	
}


function getStyleProp(node,prop){
	// Check for valid node
	if( node ) {
		// The IE way
		if( node.currentStyle )		
      return(node.currentStyle[prop]);
		// The Mozilla Way	
    if(document.defaultView.getComputedStyle)
      return(document.defaultView.getComputedStyle(node,'')[prop]);
	} // endif
	
  return(null);
}


function rgb2hex(value){
  var hex="",v,h,i;
  var regexp=/([0-9]+)[, ]+([0-9]+)[, ]+([0-9]+)/;
  var h=regexp.exec(value);
  for(i=1;i<4;i++){
    v=parseInt(h[i]).toString(16);
    if(v.length==1) hex+="0"+v;
    else hex+=v;
  } // end for
  return("#"+hex);
}

function calcBorderColor(color1,color2){
	
	if( (color1 == "transparent") ||
			(color2 == "transparent") )
	  return "transparent";
	
  var i;
	var digits1;
	var digits2;
	var x,y;
	var color_mix=new Array(3);
	
  if(color1.length==4)
	  digits1=1;
  else 
	  digits1=2;
		
  if(color2.length==4) 
	  digits2=1;
  else 
	  digits2=2;
		
  for(i=0;i<3;i++){
		
    x=parseInt(color1.substr(1+digits1*i,digits1),16);

    if(digits1==1) 
		  x=16*x+x;
			
    y=parseInt(color2.substr(1+digits2*i,digits2),16);
		
    if(digits2==1) 
		   y=16*y+y;
		
    color_mix[i]=Math.floor((x*50+y*50)/100);
		
    color_mix[i]=color_mix[i].toString(16);
		
    if(color_mix[i].length==1) 
		  color_mix[i]="0"+color_mix[i];
  }  // end for
	
  return("#"+color_mix[0]+color_mix[1]+color_mix[2]);
}


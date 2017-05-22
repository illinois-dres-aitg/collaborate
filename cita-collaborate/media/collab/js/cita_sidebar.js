/*********************************************************************** 
 *  cita_scripts.js                                                    *
 *  hide and show elements in a heirarchical navigation menu using CSS *
 *  Jon Gunderson - December 2007                                      *
 ***********************************************************************
 *
 * Generates a DHTML collapsible navigation menu given an HTML one.
 * This script operates on a navigation menu set up in the following manner,
 * where {{ }} indicates generic strings that can/should be replaced:

<div id=" {{sidenav}} "><a name=" {{nav}} "></a>
    <div class=" {{sidenav_currentarea}} ">
        <h2> {{naviagation menu title}} </h2>
        <ul id=" {{menu_id}} " title="Events">
       
            <li> <h3> {{ first subheading text }} </h3> 
                <ul title=" {{ description }} ">
                    <li><a href=" {{ href1.php }}" title=" {{ title1 }} ">  {{ link text 1 }} </a></li>
                    <li><a href=" {{ href2.php }}" title=" {{ title2 }} ">  {{ link text 2 }} </a></li>
                     etc...
                </ul>
            </li>
        
            <li> <h3> {{ second subheading text }} </h3> 
                <ul title=" {{ description }} ">
                    <li><a href=" {{ href1.php }}" title=" {{ title1 }} ">  {{ link text 1 }} </a></li>
                    <li><a href=" {{ href2.php }}" title=" {{ title2 }} ">  {{ link text 2 }} </a></li>
                     etc... 
                </ul>
            </li>
             etc... 
        </ul>
    </div>
</div>

 *
 *
 * hrefs in the list need to be absolute, not relative.  
 */

var closedArrow = str_path + "images/arrowright.gif";
var openArrow   = str_path + "images/arrowdown.gif";

var closedAlt = "Closed Menu ";
var openAlt = "Open Menu ";

function handleSidebarToggle ( id_h3, id_ul ) {

  var node_ul = document.getElementById( id_ul );
  
  if ( node_ul ) 
    if( node_ul.style.display == "block" ) {
      node_ul.style.display = "none";
    } else {
    
      node_ul.style.display = "block";

      // open the overview page 
//      var node_a = node_ul.getElementsByTagName("a")[0];
//     window.location.href = node_a.href;
      
    }  // endif

  var node_img = document.getElementById( id_h3 ).getElementsByTagName("img")[0];
  
  if ( node_img ) 
    if( node_ul.style.display == "block" ) {
      
      node_img.src = openArrow;
	  node_img.alt = openAlt;
	  
    } else {
      node_img.src = closedArrow;
			node_img.alt = closedAlt;
    }  // endif


}


function SidebarMenu( id ) {
	
   this.id = id;
	
}

SidebarMenu.prototype.init = function() {
	
	 var thispage_url = window.location.href;

	 // Check for pointers to internal links and delete if present
	 if( thispage_url.indexOf( '#' ) > 0 )
	   thispage_url = thispage_url.substring(0, thispage_url.indexOf( '#' ) );

	 // Check for CGI variables in URL and delete if present
	 if( thispage_url.indexOf( '?' ) > 0 )
	   thispage_url = thispage_url.substring(0, thispage_url.indexOf( '?' ) );

   // Check to see if there is a file name and if not add default
	 if( (thispage_url.indexOf(".php") < 0) && (thispage_url.indexOf(".html") < 0) )
	    thispage_url = thispage_url + "index.php";
			
//   alert( thispage_url );
	 
	 var thispage_flag = false;
	
   // Test if browser support getElementById
   if( !document.getElementById )
     return;
	
   this.node = document.getElementById( this.id );
	
   // check to see if a valid ID
   if( this.node ) {
		
     // If the list has H3 elements then there are dynamic menu items
     var dynamic_nodes = this.node.getElementsByTagName("h3"); 

     // add a link to make the menu open or close
     for(var i=0; i < dynamic_nodes.length; i++ ) {
			
       var node_h3 = dynamic_nodes[i];
       var node_parent = node_h3.parentNode;
			
       var node_ul = node_parent.getElementsByTagName("ul")[0];
			
       // check to see if there is a valid node
       if( node_ul ) {
				 
        var id_ul = "sidebar_ul_id_" + i;
         node_ul.id = id_ul;
				 
         var id_h3 = "sidebar_h3_id_" + i;
         node_h3.id = id_h3;
			 
         var node_anchor = document.createElement("a");
         node_anchor.setAttribute("href", "javascript:handleSidebarToggle('" + id_h3 + "','" + id_ul + "' )" );

         var node_img = document.createElement("img");
				 node_img.setAttribute("src", closedArrow);
				 node_img.setAttribute("alt", closedAlt);
				 
				 node_anchor.appendChild( node_img );

         // Mode text content from h3 to anchor

         // Get current text in H3
         var text = node_h3.innerHTML;
				 // Create a new text node for anchor content
         var node_text = document.createTextNode ( text );
				 // Copy H3 text to the Anchor text
         node_anchor.appendChild( node_text );
         // Delete current H3 content
         node_h3.innerHTML = "";
         // Add anchor to H3
         node_h3.appendChild( node_anchor );

         // See if the current sub menu is the same as the link for the current page
				 // If the same use CSS styling to mark the anchor
         var node_anchors  = node_ul.getElementsByTagName("a");

         var flag = false;
        
         for(var j=0; (j < node_anchors.length) && !thispage_flag; j++ ) {

           if( compareURLs(thispage_url, node_anchors[j].href) ) {
             node_anchors[j].className = "thisPage";
				     node_img.setAttribute("src", openArrow);
				     node_img.setAttribute("alt", openAlt);
				     flag = true;
	           thispage_flag = true;
             break;
           }  // endif

         } // endfor


         // If the link is not in the sub menu, hide the submenu
         if( flag ) 
            node_ul.style.display = "block";
				 else
            node_ul.style.display = "none";
				 
        } // endif
			
     }  // endfor
		
		// Check to see if page link has been highlighted yet

		if( !thispage_flag ) {
			
			var node_anchors = this.node.getElementsByTagName("a");
			
			for(var i = 0; i < node_anchors.length; i++ ) {
				
        if( compareURLs(thispage_url, node_anchors[i].href) ) {
          node_anchors[i].className = "thisPage";
					thispage_flag = true;
          break;
        }  // endif
				
			}  // endfor
			
		} // endif

  }  // endif

}

function compareURLs( url_1, url_2 ) {

   // Check to see if there is a file name and if not add default
	 if( (url_2.indexOf(".php") < 0) && (url_2.indexOf(".html") < 0) )
	    var url_2 = url_2 + "index.php";

  //  Test urls
  if( url_1  && url_2 ) { 

    var i = Math.min( url_1.length, url_2.length ) - 1;
		
//		alert( i  + " " + url_1.length + " " + url_1 + " " + url_2.length + " " + url_2 );

    while( i > 0 ) {
 
       if (url_1.charAt(i) == url_2.charAt(i) ) {
         i--;
       } else {
         return false;
       } // endif
        
    }  // endwhile

    return true;

  } else {

    return false;

  } // endif

}



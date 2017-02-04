django.jQuery(document).ready(function(){
	// --- удаление изначально выбраных элементов ---
	django.jQuery(".to_delete").click(function () {django.jQuery(this).remove();});

	// --- добавляю автозаполнение для уже показываемых элементов ---
	initAutocomplete();

	setTimeout(function() {
		// Ждем пока всё загрузится
		console.log(django.jQuery(".add-row td a"));

		// --- добавляю автозаполнение для новых элементов ---
		django.jQuery(".add-row td a").click( initAutocomplete );

	}, 500);

});




function initAutocomplete() {
	django.jQuery.each( django.jQuery(".to_autocomplete") , function(key, value) { 
		var obj = django.jQuery(value);
		var obj_name = obj.attr('id').replace("lookup_",""); ;
		if (obj_name.search("__prefix__")==-1){
			console.log("to_autocomplete",obj_name,value);
			obj.autocomplete("../search/").removeClass("to_autocomplete");
		}
	});
}



function showAutocompletePopup(triggeringLink) {
	var name = triggeringLink.id.replace(/^add_/, '');
	name = id_to_windowname(name);
	href = triggeringLink.href
	if (href.indexOf('?') == -1) {
		href += '?_popup=2';
	} else {
		href  += '&_popup=2';
	}
	var win = window.open(href, name, 'height=500,width=800,resizable=yes,scrollbars=yes');
	win.focus();
	return false;
}

function dismissAddAnotherPopup(win, newId, newRepr) {
	// newId and newRepr are expected to have previously been escaped by
	// django.utils.html.escape.
	newId = html_unescape(newId);
	newRepr = html_unescape(newRepr);
	var name = windowname_to_id(win.name);

	odj_name = name.replace("id_",""); 

	//console.log('Autocomplete: dismissAddAnotherPopup', name,newId, newRepr);
	//console.log(odj_name, django.jQuery('#lookup_'+odj_name));

	autocomplete_mode = django.jQuery('#lookup_'+odj_name).attr( 'autocomplete_mode' );

	//console.log(autocomplete_mode);

	if (autocomplete_mode=="ForeignKey"){
		// --- подставляем значение из попапа ---
		django.jQuery("#id_"+odj_name).val( newId );
		django.jQuery("#lookup_"+odj_name).val( newRepr );
		//console.log('added');
		win.close();
	}else if(autocomplete_mode=="ManyToMany"){
		// --- добавляю новый элемент и значение из попапа ---
		django.jQuery('<div class="to_delete deletelink"><input type="hidden" name="'+odj_name+'" value="'+newId+'"/>'+newRepr+'</div>')
		.click(function () {django.jQuery(this).remove();})
		.appendTo('#box_'+odj_name);
		// очищаем текстовое поле
		django.jQuery('#lookup_'+odj_name).val( '' );
		win.close();
	}else{
		// --- повторяем стандартное поведение, мало ли что :) ---
		newId = html_unescape(newId);
		newRepr = html_unescape(newRepr);
		var name = windowname_to_id(win.name);
		var elem = document.getElementById(name);
		if (elem) {
			if (elem.nodeName == 'SELECT') {
				var o = new Option(newRepr, newId);
				elem.options[elem.options.length] = o;
				o.selected = true;
			} else if (elem.nodeName == 'INPUT') {
				if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {
					elem.value += ',' + newId;
				} else {
					elem.value = newId;
				}
			}
		} else {
			var toId = name + "_to";
			elem = document.getElementById(toId);
			var o = new Option(newRepr, newId);
			SelectBox.add_to_cache(toId, o);
			SelectBox.redisplay(toId);
		}
		win.close();

	}
}


function autocomplete_liFormat (row, i, num) {
	var result = row[0] ;
	return result;
}

function autocomplete_delete(obj) {
	parent = django.jQuery(obj).parent();
	console.log('autocomplete_to_delete',parent);
	django.jQuery("input",parent).val( '' );
}

django.jQuery.autocomplete = function(input, options) {
	// Create a link to self
	var me = this;

	// Create jQuery object for input element
	var $input = django.jQuery(input).attr("autocomplete", "off");

	// Apply inputClass if necessary
	if (options.inputClass) $input.addClass(options.inputClass);

	// Create results
	var results = document.createElement("div");
	// Create jQuery object for results
	var $results = django.jQuery(results);
	$results.hide().addClass(options.resultsClass).css("position", "absolute");
	if( options.width > 0 ) $results.css("width", options.width);

	// Add to body element
	django.jQuery("body").append(results);

	input.autocompleter = me;

	var timeout = null;
    var prev = "";
	var active = -1;
	var cache = {};
	var keyb = false;
	var hasFocus = false;
	var lastKeyPressCode = null;

	// flush cache
	function flushCache(){
		cache = {};
		cache.data = {};
		cache.length = 0;
	};

	// flush cache
	flushCache();

	// if there is a data array supplied
	if( options.data != null ){
		var sFirstChar = "", stMatchSets = {}, row = [];

		// no url was specified, we need to adjust the cache length to make sure it fits the local data store
		if( typeof options.url != "string" ) options.cacheLength = 1;

		// loop through the array and create a lookup structure
		for( var i=0; i < options.data.length; i++ ){
			// if row is a string, make an array otherwise just reference the array
			row = ((typeof options.data[i] == "string") ? [options.data[i]] : options.data[i]);

			// if the length is zero, don't add to list
			if( row[0].length > 0 ){
				// get the first character
				sFirstChar = row[0].substring(0, 1).toLowerCase();
				// if no lookup array for this character exists, look it up now
				if( !stMatchSets[sFirstChar] ) stMatchSets[sFirstChar] = [];
				// if the match is a string
				stMatchSets[sFirstChar].push(row);
			}
		}

		// add the data items to the cache
		for( var k in stMatchSets ){
			// increase the cache size
			options.cacheLength++;
			// add to the cache
			addToCache(k, stMatchSets[k]);
		}
	}

	$input
	.keydown(function(e) {
		// track last key pressed
		lastKeyPressCode = e.keyCode;
		switch(e.keyCode) {
			case 38: // up
				e.preventDefault();
				moveSelect(-1);
				break;
			case 40: // down
				e.preventDefault();
				moveSelect(1);
				break;
			case 9:  // tab
			case 13: // return
				if( selectCurrent() ){
					// make sure to blur off the current field
					$input.get(0).blur();
					e.preventDefault();
				}
				break;
			default:
				active = -1;
				if (timeout) clearTimeout(timeout);
				timeout = setTimeout(function(){onChange();}, options.delay);
				break;
		}
	})
	.focus(function(){
		// track whether the field has focus, we shouldn't process any results if the field no longer has focus
		hasFocus = true;
	})
	.blur(function() {
		// track whether the field has focus
		hasFocus = false;
		hideResults();
	});

	hideResultsNow();

	function onChange() {
		// ignore if the following keys are pressed: [del] [shift] [capslock]
		if( lastKeyPressCode == 46 || (lastKeyPressCode > 8 && lastKeyPressCode < 32) ) return $results.hide();
		var v = $input.val();
		if (v == prev) return;
		prev = v;
		if (v.length >= options.minChars) {
			$input.addClass(options.loadingClass);
			requestData(v);
		} else {
			$input.removeClass(options.loadingClass);
			$results.hide();
		}
	};

 	function moveSelect(step) {

		var lis = django.jQuery("li", results);
		if (!lis) return;

		active += step;

		if (active < 0) {
			active = 0;
		} else if (active >= lis.size()) {
			active = lis.size() - 1;
		}

		lis.removeClass("ac_over");

		django.jQuery(lis[active]).addClass("ac_over");

		// Weird behaviour in IE
		// if (lis[active] && lis[active].scrollIntoView) {
		// 	lis[active].scrollIntoView(false);
		// }

	};

	function selectCurrent() {
		var li = django.jQuery("li.ac_over", results)[0];
		if (!li) {
			var $li = django.jQuery("li", results);
			if (options.selectOnly) {
				if ($li.length == 1) li = $li[0];
			} else if (options.selectFirst) {
				li = $li[0];
			}
		}
		if (li) {
			selectItem(li);
			return true;
		} else {
			return false;
		}
	};

	function selectItem(li) {
		if (!li) {
			li = document.createElement("li");
			li.extra = [];
			li.selectValue = "";
		}
		var v = django.jQuery.trim(li.selectValue ? li.selectValue : li.innerHTML);
		input.lastSelected = v;
		prev = v;
		$results.html("");
		$input.val(v);
		hideResultsNow();
		if (options.onItemSelect){
			setTimeout(function() { options.onItemSelect(li) }, 1);
		}else{
			autocomplete_mode = options.lookup_obj.attr('autocomplete_mode');
			if (autocomplete_mode == "ForeignKey"){
				if( li == null ) var sValue = '';
				if( !!li.extra ) var sValue = li.extra[0];
				else var sValue = li.selectValue;
				django.jQuery("input:hidden",options.lookup_obj.parent()).val( sValue );
			}else if(autocomplete_mode == "ManyToMany"){
				//if( li == null ) return
				obj_name = options.lookup_obj.attr('id').replace("lookup_",""); ;
				//console.log('obj_name',obj_name);
				// --- Создаю новый элемент ---
				django.jQuery('<div class="to_delete deletelink"><input type="hidden" name="'+obj_name+'" value="'+li.extra[0]+'"/>'+li.selectValue+'</div>')
				.click(function () {$(this).remove();})
				.appendTo("#box_"+obj_name);
				django.jQuery("#lookup_"+obj_name).val( '' );
			}
		}
	};

	// selects a portion of the input string
	function createSelection(start, end){
		// get a reference to the input element
		var field = $input.get(0);
		if( field.createTextRange ){
			var selRange = field.createTextRange();
			selRange.collapse(true);
			selRange.moveStart("character", start);
			selRange.moveEnd("character", end);
			selRange.select();
		} else if( field.setSelectionRange ){
			field.setSelectionRange(start, end);
		} else {
			if( field.selectionStart ){
				field.selectionStart = start;
				field.selectionEnd = end;
			}
		}
		field.focus();
	};

	// fills in the input box w/the first match (assumed to be the best match)
	function autoFill(sValue){
		// if the last user key pressed was backspace, don't autofill
		if( lastKeyPressCode != 8 ){
			// fill in the value (keep the case the user has typed)
			$input.val($input.val() + sValue.substring(prev.length));
			// select the portion of the value not typed by the user (so the next character will erase)
			createSelection(prev.length, sValue.length);
		}
	};

	function showResults() {
		// get the position of the input field right now (in case the DOM is shifted)
		var pos = findPos(input);
		// either use the specified width, or autocalculate based on form element
		var iWidth = (options.width > 0) ? options.width : $input.width();
		// reposition
		$results.css({
			width: parseInt(iWidth) + "px",
			top: (pos.y + input.offsetHeight) + "px",
			left: pos.x + "px"
		}).show();
	};

	function hideResults() {
		if (timeout) clearTimeout(timeout);
		timeout = setTimeout(hideResultsNow, 200);
	};

	function hideResultsNow() {
		if (timeout) clearTimeout(timeout);
		$input.removeClass(options.loadingClass);
		if ($results.is(":visible")) {
			$results.hide();
		}
		if (options.mustMatch) {
			var v = $input.val();
			if (v != input.lastSelected) {
				selectItem(null);
			}
		}
	};

	function receiveData(q, data) {
		if (data) {
			$input.removeClass(options.loadingClass);
			results.innerHTML = "";

			// if the field no longer has focus or if there are no matches, do not display the drop down
			if( !hasFocus || data.length == 0 ) return hideResultsNow();

			if (django.jQuery.browser.msie) {
				// we put a styled iframe behind the calendar so HTML SELECT elements don't show through
				$results.append(document.createElement('iframe'));
			}
			results.appendChild(dataToDom(data));
			// autofill in the complete box w/the first match as long as the user hasn't entered in more data
			if( options.autoFill && ($input.val().toLowerCase() == q.toLowerCase()) ) autoFill(data[0][0]);
			showResults();
		} else {
			hideResultsNow();
		}
	};

	function parseData(data) {
		if (!data) return null;
		var parsed = [];
		var rows = data.split(options.lineSeparator);
		for (var i=0; i < rows.length; i++) {
			var row = django.jQuery.trim(rows[i]);
			if (row) {
				parsed[parsed.length] = row.split(options.cellSeparator);
			}
		}
		return parsed;
	};

	function dataToDom(data) {
		var ul = document.createElement("ul");
		var num = data.length;

		// limited results to a max number
		if( (options.maxItemsToShow > 0) && (options.maxItemsToShow < num) ) num = options.maxItemsToShow;

		for (var i=0; i < num; i++) {
			var row = data[i];
			if (!row) continue;
			var li = document.createElement("li");
			if (options.formatItem) {
				li.innerHTML = options.formatItem(row, i, num);
				li.selectValue = row[0];
			} else {
				li.innerHTML = row[0];
				li.selectValue = row[0];
			}
			var extra = null;
			if (row.length > 1) {
				extra = [];
				for (var j=1; j < row.length; j++) {
					extra[extra.length] = row[j];
				}
			}
			li.extra = extra;
			ul.appendChild(li);
			django.jQuery(li).hover(
				function() { django.jQuery("li", ul).removeClass("ac_over"); django.jQuery(this).addClass("ac_over"); active = django.jQuery("li", ul).indexOf(django.jQuery(this).get(0)); },
				function() { django.jQuery(this).removeClass("ac_over"); }
			).click(function(e) { e.preventDefault(); e.stopPropagation(); selectItem(this) });
		}
		return ul;
	};

	function requestData(q) {
		if (!options.matchCase) q = q.toLowerCase();
		var data = options.cacheLength ? loadFromCache(q) : null;
		// recieve the cached data
		if (data) {
			receiveData(q, data);
		// if an AJAX url has been supplied, try loading the data now
		} else if( (typeof options.url == "string") && (options.url.length > 0) ){
			django.jQuery.get(makeUrl(q), function(data) {
				data = parseData(data);
				addToCache(q, data);
				receiveData(q, data);
			});
		// if there's been no data found, remove the loading class
		} else {
			$input.removeClass(options.loadingClass);
		}
	};

	function makeUrl(q) {
		var url = options.url + "?q=" + encodeURI(q);
		for (var i in options.extraParams) {
			url += "&" + i + "=" + encodeURI(options.extraParams[i]);
		}
		return url;
	};

	function loadFromCache(q) {
		if (!q) return null;
		if (cache.data[q]) return cache.data[q];
		if (options.matchSubset) {
			for (var i = q.length - 1; i >= options.minChars; i--) {
				var qs = q.substr(0, i);
				var c = cache.data[qs];
				if (c) {
					var csub = [];
					for (var j = 0; j < c.length; j++) {
						var x = c[j];
						var x0 = x[0];
						if (matchSubset(x0, q)) {
							csub[csub.length] = x;
						}
					}
					return csub;
				}
			}
		}
		return null;
	};

	function matchSubset(s, sub) {
		if (!options.matchCase) s = s.toLowerCase();
		var i = s.indexOf(sub);
		if (i == -1) return false;
		return i == 0 || options.matchContains;
	};

	this.flushCache = function() {
		flushCache();
	};

	this.setExtraParams = function(p) {
		options.extraParams = p;
	};

	this.findValue = function(){
		var q = $input.val();

		if (!options.matchCase) q = q.toLowerCase();
		var data = options.cacheLength ? loadFromCache(q) : null;
		if (data) {
			findValueCallback(q, data);
		} else if( (typeof options.url == "string") && (options.url.length > 0) ){
			django.jQuery.get(makeUrl(q), function(data) {
				data = parseData(data)
				addToCache(q, data);
				findValueCallback(q, data);
			});
		} else {
			// no matches
			findValueCallback(q, null);
		}
	}

	function findValueCallback(q, data){
		if (data) $input.removeClass(options.loadingClass);

		var num = (data) ? data.length : 0;
		var li = null;

		for (var i=0; i < num; i++) {
			var row = data[i];

			if( row[0].toLowerCase() == q.toLowerCase() ){
				li = document.createElement("li");
				if (options.formatItem) {
					li.innerHTML = options.formatItem(row, i, num);
					li.selectValue = row[0];
				} else {
					li.innerHTML = row[0];
					li.selectValue = row[0];
				}
				var extra = null;
				if( row.length > 1 ){
					extra = [];
					for (var j=1; j < row.length; j++) {
						extra[extra.length] = row[j];
					}
				}
				li.extra = extra;
			}
		}

		if( options.onFindValue ) setTimeout(function() { options.onFindValue(li) }, 1);
	}

	function addToCache(q, data) {
		if (!data || !q || !options.cacheLength) return;
		if (!cache.length || cache.length > options.cacheLength) {
			flushCache();
			cache.length++;
		} else if (!cache[q]) {
			cache.length++;
		}
		cache.data[q] = data;
	};

	function findPos(obj) {
		var curleft = obj.offsetLeft || 0;
		var curtop = obj.offsetTop || 0;
		while (obj = obj.offsetParent) {
			curleft += obj.offsetLeft
			curtop += obj.offsetTop
		}
		return {x:curleft,y:curtop};
	}
}

django.jQuery.fn.autocomplete = function(url, options, data) {
	// Make sure options exists
	options = options || {};
	// Set url as option
	options.url = url;
	// set some bulk local data
	options.data = ((typeof data == "object") && (data.constructor == Array)) ? data : null;

	lookup_obj = django.jQuery(this);
	options.lookup_obj = lookup_obj;

	options.extraParams = options.extraParams || {
		search_fields: lookup_obj.attr('search_fields'),
		app_label: lookup_obj.attr('app_label'),
		model_name: lookup_obj.attr('model_name')
	}

	//console.log(options.extraParams);

	// Set default values for required options
	options.inputClass = options.inputClass || "ac_input";
	options.resultsClass = options.resultsClass || "ac_results";
	options.lineSeparator = options.lineSeparator || "\n";
	options.cellSeparator = options.cellSeparator || "|";
	options.minChars = options.minChars || 2;
	options.delay = options.delay || 10;
	options.matchCase = options.matchCase || 0;
	options.matchSubset = options.matchSubset || 1;
	options.matchContains = options.matchContains || 1;
	options.cacheLength = options.cacheLength || 0;
	options.mustMatch = options.mustMatch || 0;
	options.extraParams = options.extraParams || {};
	options.loadingClass = options.loadingClass || "ac_loading";
	options.selectFirst = options.selectFirst || true;
	options.selectOnly = options.selectOnly || false;
	options.maxItemsToShow = options.maxItemsToShow || 10;
	options.autoFill = options.autoFill || false;
	options.width = parseInt(options.width, 10) || 0;
	options.formatItem = options.formatItem || autocomplete_liFormat

	this.each(function() {
		var input = this;
		new django.jQuery.autocomplete(input, options);
	});

	// Don't break the chain
	return this;
}

django.jQuery.fn.autocompleteArray = function(data, options) {
	return this.autocomplete(null, options, data);
}

django.jQuery.fn.indexOf = function(e){
	for( var i=0; i<this.length; i++ ){
		if( this[i] == e ) return i;
	}
	return -1;
};

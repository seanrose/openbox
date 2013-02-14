/* global $ */

$(document).ready(function() {

    function readFormValuesIntoAssArray() {
        "use strict";

        var inputs = $('#api-call :input');
        var values = {};

        $.each($('#api-call').serializeArray(), function(i, field) {
            values[field.name] = field.value;
        });

        return values;
    }

    function getParameterByName(name) {
        "use strict";

        name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
        var regexS = "[\\?&]" + name + "=([^&#]*)";
        var regex = new RegExp(regexS);
        var results = regex.exec(window.location.search);
        if(results === null) {
            return "";
        } else {
            return decodeURIComponent(results[1].replace(/\+/g, " "));
        }
    }

    function setOauth2Tokens() {
        "use strict";

        var access_token = getParameterByName("access_token");

        $("#access").text(access_token).attr("data-refresh", getParameterByName("refresh_token"));
    }

    function makeApiCall() {
        "use strict";

        $("#submit").button("loading");

        var formElements = readFormValuesIntoAssArray();
        var boxApiUrl = "https://api.box.com/2.0/";
        var editor = ace.edit("json_ace");
        var body = editor.getValue();

        $.ajax({
            type: formElements.method,
            url: boxApiUrl + formElements.url,
            data: body,
            dataType: "json",
            headers: {
                "Authorization": "Bearer " + $("#access").text()
            },
            cache: false

        }).done(function(data, textStatus, jqXHR) {
            if(jqXHR.responseText !== "") {
                var formattedResponseJson = JSON.stringify($.parseJSON(jqXHR.responseText), null, '\t');
            } else {
                var formattedResponseJson = "Empty Response";
            }
            $("#response").text(formattedResponseJson);
            $("#response_headers").text(jqXHR.getAllResponseHeaders());
            prettyPrint();
            $("#http-cat").attr("src", "http://httpcats.herokuapp.com/" + jqXHR.status);

        }).fail(function(jqXHR, textStatus, errorThrown) {

            if(errorThrown === "") {
                alert("GOT YA !");
            }

        }).always(function() {
            $("#submit").button('reset');
        });

    }

    function setupAceEditor(elemToReplace) {
        var editor = ace.edit("json_ace");
        $(elemToReplace).css("visibility", "hidden");
        editor.renderer.setShowGutter(false);
        editor.setPrintMarginColumn(false);
        editor.getSession().setMode("ace/mode/json");
    }

    $("#url").typeahead({
        source: ["folders", "files", "collaborations", "discussions", "comments", "events", "users", "search", "shared_items", "folders/ID", "files/ID", "collaborations/ID", "discussions/ID", "comments/ID", "users/ID", "folders/ID/items", "folders/trash/items", "users/me", "folders/ID/collaborations", "/files/ID/versions"]
    });

    setupAceEditor("#json_body");
    setOauth2Tokens();

    $("#api-call").submit(function(e) {
        e.preventDefault();
        makeApiCall();
        return false;
    });

    //set the link
    $('#top-link').topLink({
        min: 400,
        fadeSpeed: 500
    });
    //smoothscroll
    $('#top-link').click(function(e) {
        e.preventDefault();
        $.scrollTo(0, 300);
    });

});

$(document).delegate('#json_body', 'keydown', function(e) {
    var keyCode = e.keyCode || e.which;

    if(keyCode === 9) {
        e.preventDefault();
        var start = $(this).get(0).selectionStart;
        var end = $(this).get(0).selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        $(this).val($(this).val().substring(0, start) + "\t" + $(this).val().substring(end));

        // put caret at right position again
        $(this).get(0).selectionStart = $(this).get(0).selectionEnd = start + 1;
    }
});

//plugin
$.fn.topLink = function(settings) {
    settings = $.extend({
        min: 1,
        fadeSpeed: 200,
        ieOffset: 50
    }, settings);
    return this.each(function() {
        //listen for scroll
        var el = $(this);
        el.css('display', 'none'); //in case the user forgot
        $(window).scroll(function() {
            //stupid IE hack
            if(!$.support.hrefNormalized) {
                el.css({
                    'position': 'absolute',
                    'top': $(window).scrollTop() + $(window).height() - settings.ieOffset
                });
            }
            if($(window).scrollTop() >= settings.min) {
                el.fadeIn(settings.fadeSpeed);
            } else {
                el.fadeOut(settings.fadeSpeed);
            }
        });
    });
};
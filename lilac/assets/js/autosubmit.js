(function($) 
{
    $.fn.autosubmit = function() 
    {
       this.submit(function(e) 
       {
            var form = $(this);

            $.ajax(
            {
                type: form.attr('method'),
                url: form.attr('action'),
                data: form.serialize(),
                success:function(res)
                {  
                    var $flash = $("#flash");
                    $flash.children('div').removeClass('info error success');
                    if (res.status != 'redirect')
                    {
                        $flash = $("#flash");
                        $flash.children('div').addClass(res.status);
                        $flash.children('div').text(res.msg);
                        $flash.fadeIn(100).fadeOut(4000);    
                    }
                    else 
                    {
                        $flash = $("#flash");
                        $flash.children('div').addClass('info');
                        $flash.children('div').text(res.msg);
                        $flash.fadeIn(100).fadeOut(3000);
                        window.location.href = res.url;
                    }
                },
                error: function(jqXHR, textStatus, errorThrown) 
                {
                    // Todo : 
                }
            });
            e.preventDefault();
        });
        this.submit();
    }
})(jQuery);
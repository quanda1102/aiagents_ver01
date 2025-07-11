function updateCatg() {
    var windowWidth = $(window).width();
    var LeftWidth = $('.main .container .row .col-md-2').width();
    var RightWidth = $('#rightbar').width();
    var wH = $(window).height();
    var heightHeader = $('header').height();
    // $(".main>.container>.row>.col-md-2").css("height", wH - heightHeader).css("top", heightHeader);
    var middleWidth = 'auto';

    if (windowWidth > 1024) {
            middleWidth = windowWidth - 300 - 310 - 30; // 300 fixed LeftWidth, 310 fixed RightWidth, 30 paddingRight
    } else {
        middleWidth = windowWidth - 300 - 30;
    }

    $('.middle-col').css('width', middleWidth).attr('data-width', middleWidth);
}

$(function(){
    const $header = $('header');
    const $topHeader = $('header .top-header');
    const $footer = $('.footer-v1');
    const $sideBar = $(".main>.container>.row>.col-md-2");
    const $vjTabs = $('.vj-tabs');
    const $stickThis = $('#stickThis');
    const $stickyRightbar = $('.js-sticky');

    if ($stickyRightbar.length) $stickyRightbar.theiaStickySidebar({
                                    additionalMarginTop: 60,
                                    containerSelector: '.main',
                                    minWidth: 1034
                                });

    const offsetSticky = 60;

    const heightAdsTop = $('.ads__top').height() || 0;

    let lastScrollTop = 0;
    let ticking = false;

    function updateStickyHeader(scrollTop) {
        const footerTop = $(document).height() - $(window).height() - $footer.outerHeight();

        if (scrollTop >= heightAdsTop + 20) {
            $header.addClass('fix-header');
            $vjTabs?.addClass('fixed');
        } else {
            $header.removeClass('fix-header');
            $vjTabs?.removeClass('fixed');
        }

        if ($sideBar) {
            let heightHeader = $header.height();
            const topOffset = Math.max(heightHeader - scrollTop, 40);

            $sideBar.css({
                top: topOffset + 'px',
                bottom: 'auto',
                height: '100%',
                position: 'fixed'
            });

            if (scrollTop >= footerTop) {
                $sideBar.css({
                    bottom: $footer.outerHeight(),
                    top: 'auto',
                    height: 'auto',
                    position: 'absolute'
                });
            }

            if (!(scrollTop > lastScrollTop) && $header.hasClass('fix-header')) {
                $sideBar.css({
                    paddingTop: '60px'
                });
            } else {
                $sideBar.css({
                    paddingTop: '0'
                });
            }
        }
    }

    function updateStickyRightbar(scrollTop) {
        if (!$stickyRightbar.length) return;

        const $theia = $stickyRightbar.find('.theiaStickySidebar');
        const theiaOffset = $theia.offset();
        const theiaHeight = $theia.outerHeight();
        const theiaBottom = theiaOffset.top + theiaHeight;
        const footerTop = $footer.offset().top;

        if (theiaBottom >= footerTop - 60) {
            $theia.css({
                transform: `translateY(-${theiaBottom - footerTop}px)`,
            });
        }

        if (!(scrollTop > lastScrollTop) && $header.hasClass('fix-header')) {
            $stickyRightbar.find(".theiaStickySidebar").css({
                paddingTop: '60px'
            });
        } else {
            $stickyRightbar.find(".theiaStickySidebar").css({
                paddingTop: '0'
            });
        }
    }

    function updateStickThis(scrollTop) {
        if ($stickThis.length == 0) return;

        const stickTop = $stickThis.offset().top;
        const scrollBottom = $(document).height() - $(window).height() - scrollTop;
        const footerHeight = $footer.outerHeight();

        if (scrollTop >= stickTop - 100 && scrollBottom > footerHeight - 100) {
            $stickThis.find('.adv__content').css({ position: 'fixed', top: '45px' });
        } else {
            $stickThis.find('.adv__content').css({ position: 'static' });
        }
    }

    function onScroll() {
        const scrollTop = $(window).scrollTop();

        updateStickyHeader(scrollTop);

        if (!ticking) {
            requestAnimationFrame(() => {
                if (Math.abs(scrollTop - lastScrollTop) > 20) {
                    if (scrollTop > lastScrollTop) {
                        $topHeader.hide();
                    } else {
                        $topHeader.show();
                    }
                    lastScrollTop = scrollTop;
                }
                ticking = false;
            });
            ticking = true;
        }

        updateStickyRightbar(scrollTop);
        updateStickThis(scrollTop);
    }

    $(window).on('scroll', onScroll);

    updateCatg();
    jQuery(window).resize(function () {
        updateCatg();
    });

    $(".navbar-default .navbar-toggle").click(function(){
        $('header .navbar-collapse').toggleClass("show-menu-mobile");
        $('.main .container .row .col-md-2').removeClass("show-sidebar");
        $(".icon-menu-category").removeClass('active');
    });

    $(".close-menu-list").click(function(){
        $('.col-md-2').removeClass('show-sidebar');
    });
    
    $(".close-menu-menu").click(function(){
        $('.navbar-collapse').removeClass('show-menu-mobile');
    });

    $(".menu-desktop-sub").click(function(){
        $(this).parent().toggleClass("show-menu");
    });

    $(".icon-menu-category").click(function(){
        $('.main .container .row .col-md-2').toggleClass("show-sidebar");
        $('header .navbar-collapse').removeClass("show-menu-mobile");
        $(this).toggleClass('active');
    });

    $('.hide-tab .top').click(function () {
        $(this).parent().toggleClass('show-hide-tab');
    });

    $('.box-search .btn-search').hover(function () {
        $('.box-search').toggleClass('show-search');
    });

    $(".box-baner-commer .close-commer").click(function(){
        $(this).parent().toggle();
    });

    const $serSlider = $('.ser-slider');

    if ($serSlider.length) {
        $serSlider.slick({
            infinite: true,
            slidesToShow: 6,
            slidesToScroll: 1,
            autoplay: true,
            arrows: false,
            responsive: [
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 5,
                        slidesToScroll: 5
                    }
                },
                {
                    breakpoint: 480,
                    settings: {
                        slidesToShow: 4,
                        slidesToScroll: 4
                    }
                },
                {
                    breakpoint: 370,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 300,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                    }
                },
                {
                    breakpoint: 200,
                    settings: {
                        slidesToShow: 1,
                        slidesToScroll: 1
                    }
                }
            ]
        });
    }
    
    const $docSlider = $('.doc-slider');

    if ($docSlider.length) {
        $docSlider.slick({
            infinite: true,
            slidesToShow: 4,
            slidesToScroll: 1,
            autoplay: true,
            arrows: false,
            responsive: [
                {
                    breakpoint: 1366,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 1200,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                    }
                },
                {
                    breakpoint: 1024,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 800,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                    }
                },
                {
                    breakpoint: 768,
                    settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3
                    }
                },
                {
                    breakpoint: 480,
                    settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                    }
                },
                {
                    breakpoint: 370,
                    settings: {
                        slidesToShow: 1,
                        slidesToScroll: 1
                    }
                }
            ]
        });
    }

    function initSlider($slider) {
        $slider.slick({
            infinite: true,
            slidesToShow: 1,
            slidesToScroll: 1,
            autoplay: false,
            dots: true,
            rows: 4,
            arrows: false,
        });
    }

    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

    function handleSlider($slider) {
        if (!$slider.length) return;
        if (isMobile) {
            $slider.not('.sl-slider').addClass('sl-slider');
            initSlider($slider);
        } else {
            $slider.removeClass('sl-slider'); // Không có dấu chấm!
        }
    }

    ['.sbox-slider', '.scourse-slider'].forEach(selector => {
        handleSlider($(selector));
    });

    if (isMobile) {
		$('.footer-links').next().css('display', 'none');
    }

	$('.footer-links').click(function() {
	  $(this).next().toggle(700);
	});

	tocRender();
	
	$('.vj-toc').on('click', '.vj-toc-btn-show', function(event) {
      event.preventDefault();
      $(this).removeClass('vj-toc-btn-show').addClass('vj-toc-btn-hide').html('<i class="fa fa-minus"></i> Thu gọn');
      $(this).parent().find('ul li:nth-child(n+4)').css('display', 'block');
	});

	$('.vj-toc').on('click', '.vj-toc-btn-hide', function(event) {
      event.preventDefault();
      $(this).removeClass('vj-toc-btn-hide').addClass('vj-toc-btn-show').html('<i class="fa fa-plus"></i> Xem thêm');
      $(this).parent().find('ul li:nth-child(n+4)').css('display', 'none');
	});
})

function tocRender() {
    const $tableContents = $('.vj-toc');
    $tableContents.prepend('<div class="vj-toc-header">Nội dung</div>');
    const children = $tableContents.find('ul li');
    const countItem = children.length;

    if (countItem == 0) {
        return;
    }
    
    if (countItem > 3) {
    	$tableContents.find('ul li:nth-child(n+4)').css('display', 'none');
        $tableContents.append('<a class="vj-toc-footer vj-toc-btn-show"><i class="fa fa-plus"></i> Xem thêm</a>');
    }
    $tableContents.css('display', 'block');
}

/*--------------------- Scroll to -------------------*/
$(document).on('click', '[data-toggle="scroll"]', function(e) {
    if (typeof e != 'undefined' && typeof e.preventDefault == 'function') {
        e.preventDefault();
    }

    var $this = $(this),
        $target = $($this.data('target'));
    if ($target.length > 0) {
        var $point = $target.offset().top - 100,
            $duration = 800;
        if ($this.data('duration')) {
            $duration = $this.data('duration');
        }
        scrollTo($point, $duration);
    }
});

function scrollTo($point, $duration) {
    if (typeof $duration == 'undefined') {
        $duration = 800;
    }

    $('body,html').animate({
        scrollTop: $point
    }, $duration);
}
/*--------------------- End Scroll to -------------------*/

document.addEventListener("DOMContentLoaded", function() {
    const menuContainer = document.getElementById("scroll-menu");
    const menuLeftBtn = document.getElementById("lscroll-menu");
    const menuRightBtn = document.getElementById("rscroll-menu");

    let isDragging = false;
    let fromScrollPos = -1;
    let gotoTut = 1;

    // --- Xử lý kéo (drag scrolling) ---
    menuContainer.addEventListener("mousedown", (e) => {
        e.preventDefault();
        fromScrollPos = e.clientX; // Lấy vị trí X ban đầu của chuột
        isDragging = true; // Đánh dấu đang kéo
    });

    menuContainer.addEventListener("mousemove", (e) => {
        if (!isDragging) return;
        const currentPos = e.clientX;
        if (currentPos === fromScrollPos) return;
        e.preventDefault();
        if (e.buttons === 0) return;
        const delta = Math.abs(currentPos - fromScrollPos);
        gotoTut = 0; // Đánh dấu đã kéo để không kích hoạt link
        menuContainer.scrollLeft += currentPos < fromScrollPos ? delta : -delta;
        updateScrollButtons();
        fromScrollPos = currentPos;
    });

    menuContainer.addEventListener("mouseup", (e) => {
        e.preventDefault();
        isDragging = false;
        fromScrollPos = -1;
    });

    // Ngăn không cho link hoạt động khi kéo
    menuContainer.addEventListener("click", (e) => {
        if (gotoTut === 0) {
            e.preventDefault();
            gotoTut = 1;
        }
    });

    function scrollmenow(n) {
        menuContainer.scrollBy({
            left: n === 1 ? 100 : -100,
            behavior: 'smooth'
        });
        setTimeout(updateScrollButtons, 200);
    }

    menuLeftBtn.addEventListener("click", (e) => {
        e.preventDefault();
        scrollmenow(-1);
    });

    menuRightBtn.addEventListener("click", (e) => {
        e.preventDefault();
        scrollmenow(1);
    });

    function updateScrollButtons() {
        const currentScrollLeft = menuContainer.scrollLeft;
        menuLeftBtn.style.display = currentScrollLeft < 1 ? "none" : "flex";
        // Ẩn nút phải nếu đã cuộn hết chiều rộng của menuContainer
        menuRightBtn.style.display =
            currentScrollLeft + menuContainer.clientWidth >= menuContainer.scrollWidth ?
            "none" :
            "flex";
    }

    window.addEventListener("load", updateScrollButtons);

    const menuActiveLink = menuContainer.querySelector("li a.active");

    if (menuActiveLink) {
        menuActiveLink.scrollIntoView({ behavior: "auto", inline: "center", block: "nearest" });

        setTimeout(updateScrollButtons, 200);
    }
});


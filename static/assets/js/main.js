AOS.init({
	duration: 800,
	easing: 'slide'
});

function toggleDropdown() {
   var dropdown = document.getElementById("dropdownMenu");
   if (dropdown.style.display === "block") {
	   dropdown.style.display = "none";
   } else {
	   dropdown.style.display = "block";
   }
}

document.addEventListener('DOMContentLoaded', function() {
   // Event listener for switching to register form
   document.getElementById('registerLink').addEventListener('click', function(event) {
	   event.preventDefault();
	   openModal('SignUp');
   });

   // Event listener for switching to login form
   document.getElementById('loginLink').addEventListener('click', function(event) {
	   event.preventDefault();
	   openModal('SignIn');
   });
});

  document.addEventListener('DOMContentLoaded', function() {
    // Fungsi untuk memformat angka menjadi Rupiah
    function formatRupiah(angka, prefix) {
      var number_string = angka.toString(),
          split = number_string.split(','),
          sisa = split[0].length % 3,
          rupiah = split[0].substr(0, sisa),
          ribuan = split[0].substr(sisa).match(/\d{3}/gi);

      // Menambahkan titik jika ada ribuan
      if (ribuan) {
        separator = sisa ? '.' : '';
        rupiah += separator + ribuan.join('.');
      }

      rupiah = split[1] != undefined ? rupiah + ',' + split[1] : rupiah;
      return prefix == undefined ? rupiah : (rupiah ? 'Rp. ' + rupiah : '');
    }

    // Mengambil semua elemen dengan class "harga-item"
    var hargaItems = document.querySelectorAll('.harga-item');

    // Loop melalui setiap elemen dan format harganya
    hargaItems.forEach(function(hargaItem) {
      var harga = parseInt(hargaItem.textContent.replace('Rp. ', '').replace(/[^0-9]/g, ''));
      hargaItem.textContent = formatRupiah(harga, 'Rp. ');
    });
  });

function closeModal() {
   document.getElementById("modal").style.display = "none";
   var tabcontent = document.getElementsByClassName("tabcontent");
   for (var i = 0; i < tabcontent.length; i++) {
	   tabcontent[i].style.display = "none";
   }
}

function openModal(tabName) {
   document.getElementById("dropdownMenu").style.display = "none";
   document.getElementById("modal").style.display = "block";
   var tabcontent = document.getElementsByClassName("tabcontent");
   for (var i = 0; i < tabcontent.length; i++) {
	   tabcontent[i].style.display = "none";
   }
   document.getElementById(tabName).style.display = "block";
}

// Close the modal when the user clicks anywhere outside of it
window.onclick = function(event) {
   var modal = document.getElementById("modal");
   if (event.target == modal) {
	   closeModal();
   }
}

// Clear form inputs
function clearForm(formId) {
   document.getElementById(formId).reset();
}

(function($) {

   "use strict";

   var isMobile = {
	   Android: function() {
		   return navigator.userAgent.match(/Android/i);
	   },
		   BlackBerry: function() {
		   return navigator.userAgent.match(/BlackBerry/i);
	   },
		   iOS: function() {
		   return navigator.userAgent.match(/iPhone|iPad|iPod/i);
	   },
		   Opera: function() {
		   return navigator.userAgent.match(/Opera Mini/i);
	   },
		   Windows: function() {
		   return navigator.userAgent.match(/IEMobile/i);
	   },
		   any: function() {
		   return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
	   }
   };


   $(window).stellar({
   responsive: true,
   parallaxBackgrounds: true,
   parallaxElements: true,
   horizontalScrolling: false,
   hideDistantElements: false,
   scrollProperty: 'scroll'
 });


   var fullHeight = function() {

	   $('.js-fullheight').css('height', $(window).height());
	   $(window).resize(function(){
		   $('.js-fullheight').css('height', $(window).height());
	   });

   };
   fullHeight();

   // loader
   var loader = function() {
	   setTimeout(function() { 
		   if($('#ftco-loader').length > 0) {
			   $('#ftco-loader').removeClass('show');
		   }
	   }, 1);
   };
   loader();

   // Scrollax
  $.Scrollax();


   // Burger Menu
   var burgerMenu = function() {
	   $('body').on('click', '.js-fh5co-nav-toggle', function(event){
		   event.preventDefault();
		   if ($('#ftco-nav').is(':visible')) {
			   $(this).removeClass('active');
		   } else {
			   $(this).addClass('active');
		   }
	   });
   };
   burgerMenu();

   // Page Nav
   var clickMenu = function() {
	   $('#ftco-nav a:not([class="external"])').click(function(event){
		   var section = $(this).data('nav-section'),
			   navbar = $('#ftco-nav');
		   
		   // Hanya mencegah default jika data-nav-section ada dan elemen target ada di halaman yang sama
		   if (section && $('[data-section="' + section + '"]').length) {
			   event.preventDefault();
			   $('html, body').animate({
				   scrollTop: $('[data-section="' + section + '"]').offset().top - 70
			   }, 500);

			   if (navbar.is(':visible')) {
				   navbar.removeClass('in');
				   navbar.attr('aria-expanded', 'false');
				   $('.js-fh5co-nav-toggle').removeClass('active');
			   }
		   }
	   });
   };
   clickMenu();

   // Reflect scrolling in navigation
   var navActive = function(section) {
	   var $el = $('#ftco-nav > ul');
	   $el.find('li').removeClass('active');
	   $el.each(function(){
		   $(this).find('a[data-nav-section="' + section + '"]').closest('li').addClass('active');
	   });
   };
   navActive();

   // Menangani semua tautan untuk memastikan tautan dengan href untuk halaman lain berfungsi
   $('#ftco-nav a').on('click', function(event) {
	   var target = $(this).attr('href');
	   if (target && target.startsWith('#')) {
		   event.preventDefault();
		   var targetSection = $(target);
		   if (targetSection.length) {
			   $('html, body').animate({
				   scrollTop: targetSection.offset().top - 70
			   }, 500);
		   }
	   }
   });

   var navigationSection = function() {

	   var $section = $('section[data-section]');
	   
	   $section.waypoint(function(direction) {
			 
			 if (direction === 'down') {
			   navActive($(this.element).data('section'));
			 }
	   }, {
			 offset: '150px'
	   });

	   $section.waypoint(function(direction) {
			 if (direction === 'up') {
			   navActive($(this.element).data('section'));
			 }
	   }, {
			 offset: function() { return -$(this.element).height() + 155; }
	   });

   };
   navigationSection();
   

   var carousel = function() {
	   $('.carousel-testimony').owlCarousel({
		   autoplay: true,
		   autoHeight: true,
		   center: true,
		   loop: true,
		   items:1,
		   margin: 30,
		   stagePadding: 0,
		   nav: true,
		   dots: false,
		   navText: ['<span class="ion-ios-arrow-back">', '<span class="ion-ios-arrow-forward">'],
		   responsive:{
			   0:{
				   items: 1
			   },
			   600:{
				   items: 1
			   },
			   1000:{
				   items: 1
			   }
		   }
	   });
	   $('.carousel-project').owlCarousel({
		   autoplay: true,
		   autoHeight: true,
		   center: false,
		   loop: true,
		   items:1,
		   margin: 30,
		   stagePadding: 0,
		   nav: false,
		   dots: true,
		   navText: ['<span class="ion-ios-arrow-back">', '<span class="ion-ios-arrow-forward">'],
		   responsive:{
			   0:{
				   items: 1
			   },
			   600:{
				   items: 2
			   },
			   1000:{
				   items: 4
			   }
		   }
	   });

   };
   carousel();

   $('nav .dropdown').hover(function(){
	   var $this = $(this);
	   // 	 timer;
	   // clearTimeout(timer);
	   $this.addClass('show');
	   $this.find('> a').attr('aria-expanded', true);
	   // $this.find('.dropdown-menu').addClass('animated-fast fadeInUp show');
	   $this.find('.dropdown-menu').addClass('show');
   }, function(){
	   var $this = $(this);
		   // timer;
	   // timer = setTimeout(function(){
		   $this.removeClass('show');
		   $this.find('> a').attr('aria-expanded', false);
		   // $this.find('.dropdown-menu').removeClass('animated-fast fadeInUp show');
		   $this.find('.dropdown-menu').removeClass('show');
	   // }, 100);
   });


   $('#dropdown04').on('show.bs.dropdown', function () {
	 console.log('show');
   });

   // scroll
   var scrollWindow = function() {
	   $(window).scroll(function(){
		   var $w = $(this),
				   st = $w.scrollTop(),
				   navbar = $('.ftco_navbar'),
				   sd = $('.js-scroll-wrap');

		   if (st > 150) {
			   if ( !navbar.hasClass('scrolled') ) {
				   navbar.addClass('scrolled');	
			   }
		   } 
		   if (st < 150) {
			   if ( navbar.hasClass('scrolled') ) {
				   navbar.removeClass('scrolled sleep');
			   }
		   } 
		   if ( st > 350 ) {
			   if ( !navbar.hasClass('awake') ) {
				   navbar.addClass('awake');	
			   }
			   
			   if(sd.length > 0) {
				   sd.addClass('sleep');
			   }
		   }
		   if ( st < 350 ) {
			   if ( navbar.hasClass('awake') ) {
				   navbar.removeClass('awake');
				   navbar.addClass('sleep');
			   }
			   if(sd.length > 0) {
				   sd.removeClass('sleep');
			   }
		   }
	   });
   };
   scrollWindow();

   var isMobile = {
	   Android: function() {
		   return navigator.userAgent.match(/Android/i);
	   },
		   BlackBerry: function() {
		   return navigator.userAgent.match(/BlackBerry/i);
	   },
		   iOS: function() {
		   return navigator.userAgent.match(/iPhone|iPad|iPod/i);
	   },
		   Opera: function() {
		   return navigator.userAgent.match(/Opera Mini/i);
	   },
		   Windows: function() {
		   return navigator.userAgent.match(/IEMobile/i);
	   },
		   any: function() {
		   return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
	   }
   };

   var counter = function() {
	   
	   $('#section-counter, .hero-wrap, .ftco-counter').waypoint( function( direction ) {

		   if( direction === 'down' && !$(this.element).hasClass('ftco-animated') ) {

			   var comma_separator_number_step = $.animateNumber.numberStepFactories.separator(',')
			   $('.number').each(function(){
				   var $this = $(this),
					   num = $this.data('number');
					   console.log(num);
				   $this.animateNumber(
					 {
					   number: num,
					   numberStep: comma_separator_number_step
					 }, 7000
				   );
			   });
			   
		   }

	   } , { offset: '95%' } );

   }
   counter();


   var contentWayPoint = function() {
	   var i = 0;
	   $('.ftco-animate').waypoint( function( direction ) {

		   if( direction === 'down' && !$(this.element).hasClass('ftco-animated') ) {
			   
			   i++;

			   $(this.element).addClass('item-animate');
			   setTimeout(function(){

				   $('body .ftco-animate.item-animate').each(function(k){
					   var el = $(this);
					   setTimeout( function () {
						   var effect = el.data('animate-effect');
						   if ( effect === 'fadeIn') {
							   el.addClass('fadeIn ftco-animated');
						   } else if ( effect === 'fadeInLeft') {
							   el.addClass('fadeInLeft ftco-animated');
						   } else if ( effect === 'fadeInRight') {
							   el.addClass('fadeInRight ftco-animated');
						   } else {
							   el.addClass('fadeInUp ftco-animated');
						   }
						   el.removeClass('item-animate');
					   },  k * 50, 'easeInOutExpo' );
				   });
				   
			   }, 100);
			   
		   }

	   } , { offset: '95%' } );
   };
   contentWayPoint();

   // magnific popup
   $('.image-popup').magnificPopup({
   type: 'image',
   closeOnContentClick: true,
   closeBtnInside: false,
   fixedContentPos: true,
   mainClass: 'mfp-no-margins mfp-with-zoom', // class to remove default margin from left and right side
	gallery: {
	 enabled: true,
	 navigateByImgClick: true,
	 preload: [0,1] // Will preload 0 - before current, and 1 after the current image
   },
   image: {
	 verticalFit: true
   },
   zoom: {
	 enabled: true,
	 duration: 300 // don't foget to change the duration also in CSS
   }
 });

 $('.popup-youtube, .popup-vimeo, .popup-gmaps').magnificPopup({
   disableOn: 700,
   type: 'iframe',
   mainClass: 'mfp-fade',
   removalDelay: 160,
   preloader: false,

   fixedContentPos: false
 });




 
})(jQuery);
(function() {
  const slider = document.getElementById('reviewsSlider');
  if (!slider) return;
  
  const container = slider.closest('.reviews-slider-container');
  const prevBtn = container.querySelector('.slider-prev-btn');
  const nextBtn = container.querySelector('.slider-next-btn');
  const scrollAmount = 350;
  
  nextBtn?.addEventListener('click', () => {
    slider.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  });
  
  prevBtn?.addEventListener('click', () => {
    slider.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  });
})();


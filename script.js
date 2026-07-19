const header = document.querySelector('.site-header');
const menuButton = document.querySelector('.menu-toggle');
const navigation = document.querySelector('.site-nav');

const updateHeader = () => header.classList.toggle('scrolled', window.scrollY > 20);
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

menuButton.addEventListener('click', () => {
  const open = navigation.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});

navigation.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  navigation.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
}));

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -30px' });

document.querySelectorAll('.reveal').forEach((element) => observer.observe(element));

const productSelect = document.querySelector('#product-select');
document.querySelectorAll('.inquiry-trigger').forEach((button) => {
  button.addEventListener('click', () => {
    productSelect.value = button.dataset.product;
    document.querySelector('#contact').scrollIntoView({ behavior: 'smooth' });
    window.setTimeout(() => document.querySelector('[name="message"]').focus(), 650);
  });
});

document.querySelector('#quote-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const lines = [
    'Hello VSTAR, I would like to request a quotation.',
    '',
    `Name: ${data.get('name')}`,
    `Company: ${data.get('company') || 'Not provided'}`,
    `Email: ${data.get('email') || 'Not provided'}`,
    `Product category: ${data.get('product')}`,
    `Requirement: ${data.get('message')}`,
  ];
  window.open(`https://wa.me/8615161501775?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
});

document.querySelector('#year').textContent = new Date().getFullYear();

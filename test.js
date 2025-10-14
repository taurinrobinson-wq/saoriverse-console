import { fetchData } from './supabaseClient.js';

fetchData().then(data => {
  console.log('Fetched data:', data);
});
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

(async () => {
  try {
    // Define input and output file paths
    const paramsFilePath = path.join(__dirname, 'params.txt');
    const outputFilePath = path.join(__dirname, 'output.txt');

    // Read parameters from params.txt
    if (!fs.existsSync(paramsFilePath)) {
      console.error('params.txt not found. Exiting...');
      return;
    }
    const params = fs.readFileSync(paramsFilePath, 'utf8').split('\n').map(param => param.trim());

    // Define the URL to crawl
    const url = 'https://adfs3.culinary.edu/adfs/ls/?client-request-id=7e9b8e9a-29ed-4b0c-9117-3ff5f36e971f&username=&wa=wsignin1.0&wtrealm=urn%3afederation%3aMicrosoftOnline&wctx=estsredirect%3d2%26estsrequest%3drQQIARAA42KwMsooKSkottLXTy7NycxLLKrMzCsuySwpLUnVK85ILEotyM_MK9FLzs_Vyy9Kz0wBsYqEuARm9c2ue6vJ4z1R3P7r57zp8rMYeWAG6KWmlK5itCfWXP3izJLUYv2A_KKSxJzwzKLUtKLE3FTDC4yMLxgZbzEJ-hele6aEF7ulpqQWJZZk5uddYBF4xcJjwGzFwcElwCDBoMDwg4VxESvQUQd2dfJvlPH23T3ZeseXdG6GU6z6Tt6VFYkp4SVhhYHaacERPoHGJvlGeUFpHulGYZ7hhll5kUZ5iWbFIdquBrYWVoYT2IQmsDGdYmP4wMbYwc4wi51hFyelPjnAy_CD79vN67cbJp5557FBgOGBAAMA0#'; // Replace with your URL

    // First method: Extract all <input> elements
    const browser1 = await puppeteer.launch({ headless: true });
    const page1 = await browser1.newPage();
    console.log(`Navigating to ${url} using the first method...`);
    await page1.goto(url, { waitUntil: 'domcontentloaded' });

    const inputs = await page1.evaluate(() => {
      return Array.from(document.querySelectorAll('input')).map(input => ({
        id: input.getAttribute('id'),
        name: input.getAttribute('name'),
        type: input.getAttribute('type'),
        html: input.outerHTML,
      }));
    });

    const matches = [];
    inputs.forEach(input => {
      if (!input.id && !input.name) return; // Skip inputs without id or name
      params.forEach(param => {
        if (param === input.id || param === input.name) {
          matches.push({
            param,
            type: input.type,
            id: input.id,
            name: input.name,
            html: input.html,
          });
        }
      });
    });

    await browser1.close();

    // Check if matches are found using the first method
    if (matches.length > 0) {
      console.log('Matches found using the first method. Writing to output.txt...');
      fs.writeFileSync(outputFilePath, JSON.stringify(matches, null, 2));
      console.log(`Matches saved to ${outputFilePath}`);
      return;
    }

    console.log('No matches found using the first method. Retrying with the second method...');

    // Second method: Relaunch browser and target specific <form> or elements
    const browser2 = await puppeteer.launch({ headless: false }); // Open browser for second method
    const page2 = await browser2.newPage();
    console.log(`Navigating to ${url} using the second method...`);
    await page2.goto(url, { waitUntil: 'networkidle0' }); // Wait for network activity to idle

    console.log('Waiting for the form...');
    await page2.waitForSelector('form.auth-login-form'); // Wait for the form's presence

    const formInputs = await page2.evaluate(() => {
      return Array.from(document.querySelectorAll('form.auth-login-form input')).map(input => ({
        id: input.getAttribute('id'),
        name: input.getAttribute('name'),
        type: input.getAttribute('type'),
        placeholder: input.getAttribute('placeholder'),
        html: input.outerHTML,
      }));
    });

    formInputs.forEach(input => {
      params.forEach(param => {
        if (param === input.id || param === input.name) {
          matches.push({
            param,
            type: input.type,
            id: input.id,
            name: input.name,
            placeholder: input.placeholder,
            html: input.html,
          });
        }
      });
    });

    // Save matches after the second method
    if (matches.length > 0) {
      console.log('Matches found using the second method. Writing to output.txt...');
      fs.writeFileSync(outputFilePath, JSON.stringify(matches, null, 2));
      console.log(`Matches saved to ${outputFilePath}`);
    } else {
      console.log('No matches found using either method.');
    }

    await browser2.close(); // Close the second browser session
    console.log('Browser closed.');
  } catch (err) {
    console.error('Error:', err.message);
  }
})();

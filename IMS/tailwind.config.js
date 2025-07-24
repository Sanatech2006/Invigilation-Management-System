module.exports = {
  content: [
    // Scan all HTML templates
    "./templates/**/*.html",           // Base templates
    "./templates/base/**/*.html",      // base/head.html
    "./templates/dashboard/**/*.html", // dashboard.html
    // Include JS files if using dynamic classes
    "./static/src/**/*.js",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
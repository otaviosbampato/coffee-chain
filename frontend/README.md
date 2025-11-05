# CoffeeChain Frontend

Beautiful, dynamic web interface for the Coffee Traceability Blockchain system.

## 🎨 Features

- **Modern Design**: Coffee-themed color palette with smooth animations
- **Responsive**: Works on desktop, tablet, and mobile devices
- **Role-Based UI**: Different interfaces for Fiscalizers and Clients
- **Real-Time**: Live blockchain data and validation
- **Interactive**: Dynamic forms, search, and data visualization

## 📁 Files

```
frontend/
├── index.html    # Main HTML structure
├── styles.css    # Beautiful CSS styling
└── app.js        # JavaScript functionality
```

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)

From the project root:
```bash
./start.sh
```

This will:
1. Start the backend API server
2. Open the frontend in your browser automatically

### Option 2: Manual Start

1. **Start the Backend API:**
```bash
cd /home/sbnote/Desktop/blockchain
source venv/bin/activate
python3 api_blockchain.py
```

2. **Open the Frontend:**
Open `index.html` in your web browser:
```bash
xdg-open frontend/index.html
# or simply double-click the file
```

## 🔐 Test Credentials

**Fiscalizers (can create entries):**
- Username: `fiscalizer1`
- Password: `fisc123`

**Clients (read-only access):**
- Username: `client1`
- Password: `client123`

## 📱 Features by Role

### Fiscalizers Can:
- ✅ Create new coffee entries
- ✅ Query all coffee data
- ✅ Validate blockchain
- ✅ Export blockchain

### Clients Can:
- ✅ Query coffee by Batch ID
- ✅ Query coffee by Origin/Farm
- ✅ View all entries
- ✅ Validate blockchain integrity
- ✅ Verify authenticity via blockchain hash

## 🎯 How to Use

### 1. Login
Click the "Login" button in the top right or "Get Started" on the home page.

### 2. Create Entry (Fiscalizers Only)
1. Navigate to "Dashboard"
2. Fill in the coffee entry form
3. Click "Add to Blockchain"
4. Entry is added with cryptographic proof

### 3. Query Coffee (All Users)
1. Navigate to "Query Coffee"
2. Choose search method:
   - **By Batch ID**: Search specific batch
   - **By Origin**: Find all coffee from a farm
   - **All Entries**: View everything
3. Click Search
4. View detailed results with blockchain verification

### 4. Check Blockchain (All Users)
1. Navigate to "Blockchain"
2. View real-time statistics
3. Click "Validate Chain" to verify integrity
4. See proof-of-work details

## 🎨 Design Highlights

### Color Palette
- **Primary**: Coffee brown (#6F4E37)
- **Secondary**: Chocolate (#D2691E)
- **Accent**: Tan (#CD853F)
- **Background**: Cream gradient

### Animations
- Smooth page transitions
- Floating coffee icon
- Hover effects on cards
- Toast notifications
- Loading spinners

### UI Components
- Navigation bar with active state
- Modal dialogs for login
- Tabbed search interface
- Card-based layouts
- Form validation
- Error/success messages

## 🔧 Customization

### Change API URL
Edit `app.js`, line 2:
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

### Modify Colors
Edit `styles.css`, `:root` section:
```css
:root {
    --primary: #6F4E37;
    --secondary: #D2691E;
    /* ... more colors */
}
```

### Add New Features
The code is modular and well-commented. Key sections:
- **Navigation**: `initNavigation()`
- **Authentication**: `initAuth()`, `handleLogin()`
- **Forms**: `initForms()`, `handleCreateEntry()`
- **Search**: `initSearch()`, `searchByBatch()`, etc.
- **Blockchain**: `loadBlockchainInfo()`, `validateBlockchain()`

## 📊 Data Flow

```
User Action → Frontend (app.js) → API Request → Backend → Blockchain
                                              ↓
User Interface ← JSON Response ← API Gateway ← Database
```

## 🌐 Browser Compatibility

Tested on:
- ✅ Chrome/Chromium (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

Requires modern browser with ES6+ support.

## 🐛 Troubleshooting

### "Could not connect to server"
- Make sure the backend API is running on port 5000
- Check console for errors (F12)
- Verify CORS is enabled in `api_blockchain.py`

### "Please login first"
- Click the Login button
- Use test credentials provided above
- Token is stored in localStorage

### Forms not submitting
- Check required fields (marked with *)
- Open browser console (F12) for errors
- Ensure API server is running

### Search returns no results
- Verify the batch ID or origin name is correct
- Make sure entries exist in the blockchain
- Check that you're logged in

## 📝 Technical Details

### Technologies Used
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with variables, grid, flexbox
- **JavaScript (ES6+)**: Async/await, fetch API, modules
- **Font Awesome**: Icons
- **No frameworks**: Pure vanilla JavaScript

### Security Features
- JWT token authentication
- Secure password handling (sent via HTTPS in production)
- Role-based access control
- XSS protection via proper escaping
- CORS configuration

### Performance
- Lazy loading of data
- Smooth animations with CSS transforms
- Efficient DOM manipulation
- LocalStorage for token persistence

## 🚀 Production Deployment

### Before deploying:

1. **Enable HTTPS**: Never use HTTP in production
2. **Update API URL**: Point to production backend
3. **Minify assets**: Use tools to compress CSS/JS
4. **Add analytics**: Track user behavior
5. **Error tracking**: Implement Sentry or similar
6. **CDN**: Host static files on CDN for speed

### Deployment options:
- **Static hosting**: Netlify, Vercel, GitHub Pages
- **Web server**: Nginx, Apache
- **Cloud**: AWS S3 + CloudFront, Azure Static Web Apps

## 📚 Learning Resources

- [MDN Web Docs](https://developer.mozilla.org/)
- [CSS Tricks](https://css-tricks.com/)
- [JavaScript.info](https://javascript.info/)

## 🤝 Contributing

This is a private project. For modifications:
1. Test thoroughly
2. Maintain code style
3. Update documentation
4. Comment complex logic

## 📄 License

Copyright © 2025. All rights reserved.

---

**Built with ❤️ for transparent coffee supply chains**

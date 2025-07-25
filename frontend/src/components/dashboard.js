import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'
import './dashboard.css';
import jwt_decode from 'jwt-decode';



function Dashboard() {
    const [loans, setLoans] = useState([])
    const [showForm, setShowForm] = useState(false);
    const [recentActivity, setRecentActivity] = useState([]);
    const [showPaymentForm, setShowPaymentForm] = useState(false);
    const [selectedLoanId, setSelectedLoanId] = useState('');
    const [paymentAmount, setPaymentAmount] = useState('');
    const [username, setUserName] = useState('');
    const [dueLoans, setDueLoans] = useState([]);
    const [showAllLoans, setShowAllLoans] = useState(false);
    const [stats, setStats] = useState({
      totalClients: 0,
      activeLoans: 0,
      upcomingDue: 0,
      overdue: 0,
      totalAmount: 0
    });
    
    const token = localStorage.getItem('token');
    const navigate = useNavigate();
    
    useEffect(() => {
        if(!token) {
            navigate('/');
    }
        else {
          fetch('https://loantracker-backend.onrender.com/api/user', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
            .then(res => res.json())
            .then(data => {
              console.log("User API response:", data);
              setUserName(data.name.split(" ")[0] || 'User');
            })
            .catch(err => console.error('Error fetching user info:', err));
        }
  }, [navigate]);
    useEffect(() => {
  const token = localStorage.getItem('token');

  fetch('https://loantracker-backend.onrender.com/api/loans/due-soon', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
    .then(res => res.json())
    .then(data => setDueLoans(data))
    .catch(err => console.error('Error fetching due loans:', err));
}, []);
  // 🌐 Fetch all loans from Flask backend
    useEffect(() => {
        const token = localStorage.getItem('token');

        fetch('https://loantracker-backend.onrender.com/api/loans', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
          .then(res => res.json())
          .then(data => setLoans(data))
          .catch(err => console.error('Error fetching loans:', err));
        
        fetch('https://loantracker-backend.onrender.com/api/stats', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
          .then(res => {
            if (!res.ok) throw new Error("Failed to fetch stats");
            return res.json(); 
          })
          .then(data => setStats(data))
          .catch(err => console.error('Error fetching stats:', err));
    }, []);
    const handleSendReminders = () => {
      const token = localStorage.getItem('token');
      fetch('https://loantracker-backend.onrender.com/api/send-reminders', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then(res => res.json())
        .then(data => alert(data.message))
        .catch(err => {
          console.error('Failed to send reminders:', err);
          alert('Error sending reminders.');
        });
  };
    const handleAddLoanClick = () => {
        setShowForm(!showForm);
    };

    const handleSubmitLoan = (e) => {
      e.preventDefault();
      const token = localStorage.getItem('token');
      const formData = new FormData(e.target);

      const newLoan = {
          name: formData.get('name'),
          amount: parseFloat(formData.get('amount')),
          // due: formData.get('due'),
          interest: formData.get('interest'),
          duration: formData.get('duration'),
          phone: formData.get('phonenumber'),
          email: formData.get('email'),
          status: 'Pending' // you can make this dynamic later
      };
      fetch('https://loantracker-backend.onrender.com/api/loan', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(newLoan)
      })
    .then(res => {
      if (!res.ok) throw new Error("Loan submission failed");
      return res.json();
    })
    .then(data => {
        console.log('response:', data);
    
    // Store new loan in loans array
      fetch('https://loantracker-backend.onrender.com/api/loans', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
          .then(res => res.json())
          .then(updatedLoans => setLoans(updatedLoans))
          .catch(err => console.error('Error refreshing loans:', err));
            
        const newEntry = `${newLoan.name} registered for ₦${newLoan.amount} due on ${newLoan.due} at an interest of $${newLoan.interest}%`;
        setRecentActivity(prev => [newEntry, ...prev]);

        fetch('https://loantracker-backend.onrender.com/api/stats', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
          .then(res => res.json())
          .then(updatedStats => setStats(updatedStats))
          .catch(err => console.error('Failed to update stats:', err));

        e.target.reset();
        setShowForm(false);
    })
    .catch(err => {
        console.error('Error sending data to backend:', err);
        alert('Failed to save loan. Try again')
    });
    };

    const handleExport = async () => {
      try {
        const token = localStorage.getItem('token');

        // 1. call the endpoint **with** the JWT header
        const res = await fetch(
          'https://loantracker-backend.onrender.com/api/export',
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        if (!res.ok) throw new Error('Network response was not ok');

        // 2. treat the reply as a Blob
        const blob = await res.blob();

        // 3. build a temporary download link
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href      = url;
        a.download  = 'loan_export.csv';
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error('CSV export failed:', err);
        alert('Export failed. Are you still logged-in?');
      }
};

    const handleLogout = () => {
    const confirmLogout = window.confirm('Are you sure you want to logout?');
    if (confirmLogout) {
      localStorage.clear(); // clears all localStorage
      setLoans([]);
      setStats({
        totalClients: 0,
        activeLoans: 0,
        upcomingDue: 0,
        overdue: 0,
        totalAmount: 0
      });
      setUserName('');
      navigate('/');
    }
  };

    return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h2>Welcome, {username || 'User'}</h2>
        <button className="logout-btn" onClick={handleLogout}>Logout</button>
      </header>

      <section className="stats-grid">
        <div className="stat-card">
          <h4>Total Clients</h4>
          <p>{stats.totalClients}</p>
        </div>
        <div className="stat-card">
          <h4>Active Loans</h4>
          <p>{stats.activeLoans}</p>
        </div>
        <div className="stat-card">
          <h4>Upcoming Due</h4>
          <p>{stats.upcomingDue}</p>
        </div>
        <div className="stat-card">
          <h4>Overdue Loans</h4>
          <p>{stats.overdue}</p>
        </div>
        <div className="stat-card">
        <h4>Total Amount Lent</h4>
        <p>₦{stats.totalAmount}</p>
      </div>
      </section>

      <section className="actions-grid">
        <button onClick={handleAddLoanClick}>
            {showForm ? 'Cancel' : '+ Add Loan'}
        </button>
        <button on onClick={()=> setShowAllLoans(prev => !prev)}>
          {showAllLoans ? 'Hide Loans' : 'View All Loans'}</button>
        <button onClick={handleSendReminders}>Send Reminders</button>
        <button onClick={handleExport}>Export to CSV</button>
        <button onClick={() => setShowPaymentForm(true)}>
          Make Payment
        </button>
      </section>
      
      {showForm && (
        <form className="loan-form" onSubmit={handleSubmitLoan}>
            <h3>Register New Loan</h3>
            <input type="text" name="name" placeholder="Borrower Name" required />
            <input type="number" name="amount" placeholder="Loan Amount" required />
            {/* <input type="date" name="due" placeholder="Due Date" required /> */}
            <input type="number" name="interest" placeholder="Interest" required />
            <input type="tel" name="phonenumber" placeholder="Phone Number" required />
            <input type="text" name="email" placeholder="E-mail" required />
            <input type="number" name="duration" placeholder="Duration" required />
            <button type="submit"> Submit Loan</button>
        </form>
      )}
      {showPaymentForm && (
  <div className="payment-form-container">
    <h3>Record a Payment</h3>
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        fetch(`https://loantracker-backend.onrender.com/api/payment`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ loan_id: selectedLoanId, amount_paid: paymentAmount })
        })
          .then(res => res.json())
          .then(data => {
            alert(data.message || 'Payment recorded');
            setShowPaymentForm(false);
            setPaymentAmount('');
            setSelectedLoanId('');

            // Refresh loans and stats
            fetch('https://loantracker-backend.onrender.com/api/loans', {
              headers: { 'Authorization': `Bearer ${token}` }
            })
              .then(res => res.json())
              .then(data => setLoans(data));
            

                  // Refresh due loans
            fetch('https://loantracker-backend.onrender.com/api/loans/due-soon', {
              headers: { 'Authorization': `Bearer ${token}` }
            })
              .then(res => res.json())
              .then(data => setDueLoans(data));

            fetch('https://loantracker-backend.onrender.com/api/stats', {
              headers: { 'Authorization': `Bearer ${token}` }
            })
              .then(res => res.json())
              .then(data => setStats(data));
          })
          .catch(err => {
            console.error(err);
            alert('Error recording payment');
          });
      }}
    >
      <label>Select Loaner</label>
      <select
        value={selectedLoanId}
        onChange={(e) => setSelectedLoanId(e.target.value)}
        required
      >
        <option value="">-- Select --</option>
        {loans.map((loan) => (
          <option key={loan.id} value={loan.id}>
            {loan.name} — ₦{loan.amount} borrowed
          </option>
        ))}
      </select>

      <label>Payment Amount (₦)</label>
      <input
        type="number"
        value={paymentAmount}
        onChange={(e) => setPaymentAmount(e.target.value)}
        required
      />

      <button type="submit">Submit</button>
      <button type="button" onClick={() => setShowPaymentForm(false)}>Cancel</button>
    </form>
  </div>
    )}

      <section className="recent-activity">
        <h3>Recent Activity</h3>
        <ul>
            {recentActivity.map((entry, index) => (
                <li key={index}>{entry}</li>
            ))}
        </ul>

      </section>
            {showAllLoans && (
  <section className="loan-table">
    <h3>All Loans</h3>
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Account Number</th>
          <th>Original Amount</th>
          <th>Amount Left</th>
          <th>Interest (%)</th>
          <th>Start Date</th>
          <th>Due Date</th>
        </tr>
      </thead>
      <tbody>
        {loans.map((loan, index) => (
          <tr key={index}>
            <td>{loan.name}</td>
            <td>{loan.account_number}</td>
            <td>₦{loan.amount}</td>
            <td>₦{loan.amount_left}</td>
            <td>{loan.interest}%</td>
            <td>{loan.registered_date}</td>
            <td>{loan.due ? new Date(loan.due).toLocaleDateString() : 'N/A'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </section>
)}
     <section className="loan-table">
  <h3>Loans Due This Week</h3>
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Amount Borrowed</th>
        <th>Amount Left</th>
        <th>Last Payment</th>
        <th>Last Payment Date</th>
        <th>Due Date</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      {Array.isArray(dueLoans) && dueLoans.map((loan, index) => (
        <tr key={index}>
          <td>{loan.name}</td>
          <td>₦{loan.original_amount || loan.amount}</td>
          <td>₦{loan.amount_left}</td>
          <td>₦{loan.last_payment_amount || 0}</td>
          <td>{loan.last_payment_date ? new Date(loan.last_payment_date).toLocaleDateString() : 'N/A'}</td>
          <td>{loan.due ? new Date(loan.due).toLocaleDateString() : 'N/A'}</td>
          <td>{loan.status}</td>
    </tr>
      ))}
    </tbody>
  </table>
</section>
    </div>
    ); 
};

export default Dashboard;
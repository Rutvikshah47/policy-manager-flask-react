import React from 'react';
import { useState, useEffect } from "react";
import axios from "axios";
import './App.css';


function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [policies, setPolicies] = useState([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [form, setForm] = useState({});
  const [file, setFile] = useState(null);
  console.log("App component rendered");
  const login = async () => {
    console.log("Attempting login...");
    const res = await axios.post("http://localhost:5000/login", { username: "ramya", password: "ramya.123" });
    console.log("Login response:", res.data);
    if (res.data.status === "success") setLoggedIn(true);
  };

  const fetchPolicies = async () => {
    console.log("Fetching policies...");
    const res = await axios.get("http://localhost:5000/get_policies", { params: { search, status } });
    console.log("Policies fetched:", res.data);
    setPolicies(res.data);
  };

  const addPolicy = async () => {
    console.log("Adding new policy...");
    const data = new FormData();
    Object.entries(form).forEach(([key, value]) => data.append(key, value));
    data.append("file", file);
    await axios.post("http://localhost:5000/add_policy", data);
    fetchPolicies();
  };

  const exportData = () => {
    console.log("Exporting data...");
    window.open("http://localhost:5000/export", '_blank');
  };

  useEffect(() => { if (loggedIn) fetchPolicies(); }, [loggedIn, search, status]);

  if (!loggedIn) return <button onClick={login}>Login</button>;

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-2">Policy Manager</h1>
      <input placeholder="Search" onChange={e => setSearch(e.target.value)} className="border p-2 mr-2" />
      <select onChange={e => setStatus(e.target.value)} className="border p-2">
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="expired">Expired</option>
      </select>
      <button onClick={exportData} className="ml-2 p-2 bg-blue-500 text-white">Export to Excel</button>

      <div className="mt-4">
        <input placeholder="Customer Name" onChange={e => setForm({...form, customer_name: e.target.value})} className="border p-2 mr-2" />
        <input placeholder="Car Number" onChange={e => setForm({...form, car_number: e.target.value})} className="border p-2 mr-2" />
        <input placeholder="Policy Name" onChange={e => setForm({...form, policy_name: e.target.value})} className="border p-2 mr-2" />
        <input type="date" onChange={e => setForm({...form, expiry_date: e.target.value})} className="border p-2 mr-2" />
        <input placeholder="Premium Amount" onChange={e => setForm({...form, premium_amount: e.target.value})} className="border p-2 mr-2" />
        <input type="file" onChange={e => setFile(e.target.files[0])} className="border p-2 mr-2" />
        <button onClick={addPolicy} className="p-2 bg-green-500 text-white">Add Policy</button>
      </div>

      <div className="mt-6">
        {policies.map((p, idx) => (
          <div key={idx} className="border p-4 mb-2 rounded">
            <p><strong>{p.policy_name}</strong> for {p.customer_name} ({p.car_number})</p>
            <p>Expiry: {p.expiry_date} | Premium: ₹{p.premium_amount}</p>
            <a href={p.file_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Download</a>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;

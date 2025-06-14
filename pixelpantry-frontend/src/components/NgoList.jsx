import { useState, useEffect } from "react";
import "./NgoList.css";


export default function NgoList() {
  const [ngos, setNgos] = useState([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("http://localhost:5000/ngos") // Adjust if backend is deployed elsewhere
      .then((response) => response.json())
      .then((data) => setNgos(data))
      .catch((error) => console.error("Error fetching NGOs:", error));
  }, []);

  const filteredNgos = ngos.filter((ngo) =>
    ngo.name.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">NGO Directory</h1>
      <input
        type="text"
        placeholder="Search NGOs..."
        className="w-full p-2 border rounded mb-4"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      <ul className="space-y-4">
        {filteredNgos.map((ngo) => (
          <li key={ngo.ngo_id} className="p-4 border rounded shadow">
            <h2 className="text-lg font-semibold">{ngo.name}</h2>
            <p className="text-sm text-gray-600">📍 Location: ({ngo.location.latitude}, {ngo.location.longitude})</p>
            <p className="text-sm text-blue-600">📧 {ngo.contact}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

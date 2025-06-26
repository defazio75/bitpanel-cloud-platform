// src/components/ui/Chart.jsx

export default function Chart({ title = 'Chart', data }) {
  return (
    <div className="bg-white border rounded p-4">
      <h3 className="font-bold mb-2">{title}</h3>
      <div className="text-gray-500 text-sm">[Chart placeholder]</div>
    </div>
  );
}

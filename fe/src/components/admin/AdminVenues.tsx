import { useState, useEffect } from 'react';
import { Edit2Icon, Trash2Icon, PlusIcon, XIcon } from 'lucide-react';
import { venueApi } from '../../services/api';

export function AdminVenues() {
  const [venues, setVenues] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVenue, setEditingVenue] = useState<any>(null);
  const [formData, setFormData] = useState({ name: '', address: '', capacity: 0 });

  const fetchVenues = async () => {
    try {
      const data = await venueApi.getAll();
      setVenues(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchVenues();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingVenue) {
        await venueApi.update(editingVenue.id, formData);
      } else {
        await venueApi.create(formData);
      }
      setIsModalOpen(false);
      setEditingVenue(null);
      setFormData({ name: '', address: '', capacity: 0 });
      fetchVenues();
    } catch (error) {
      alert("Lỗi khi lưu địa điểm");
      console.error(error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Bạn có chắc chắn muốn xoá địa điểm này? (Sẽ xoá cả sự kiện thuộc địa điểm)")) {
      try {
        await venueApi.delete(id);
        fetchVenues();
      } catch (e) {
        alert("Lỗi khi xoá");
        console.error(e);
      }
    }
  };

  const openEditModal = (venue: any) => {
    setEditingVenue(venue);
    setFormData({ name: venue.name, address: venue.address, capacity: venue.capacity });
    setIsModalOpen(true);
  };

  const openAddModal = () => {
    setEditingVenue(null);
    setFormData({ name: '', address: '', capacity: 0 });
    setIsModalOpen(true);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-navy-900">Quản lý Địa điểm</h3>
        <button 
          onClick={openAddModal}
          className="flex items-center gap-2 bg-navy-900 text-white px-4 py-2 rounded-xl hover:bg-navy-800 transition-colors"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Thêm địa điểm</span>
        </button>
      </div>

      <div className="bg-white border border-navy-100 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-navy-50 text-navy-600 font-medium border-b border-navy-100">
            <tr>
              <th className="px-6 py-4">Tên địa điểm</th>
              <th className="px-6 py-4">Địa chỉ</th>
              <th className="px-6 py-4 text-right">Sức chứa</th>
              <th className="px-6 py-4 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-50">
            {venues.map((v) => (
              <tr key={v.id} className="hover:bg-navy-50/50 transition-colors">
                <td className="px-6 py-4 text-navy-900 font-medium">{v.name}</td>
                <td className="px-6 py-4 text-navy-600">{v.address}</td>
                <td className="px-6 py-4 text-navy-600 text-right">{v.capacity}</td>
                <td className="px-6 py-4 flex items-center justify-end gap-2">
                  <button 
                    onClick={() => openEditModal(v)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Edit2Icon className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDelete(v.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2Icon className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {venues.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-navy-400">
                  Chưa có dữ liệu
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-navy-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden">
            <div className="flex justify-between items-center px-6 py-4 border-b border-navy-50">
              <h4 className="text-lg font-bold text-navy-900">
                {editingVenue ? 'Sửa Địa điểm' : 'Thêm Địa điểm mới'}
              </h4>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-navy-400 hover:text-navy-600 transition-colors"
              >
                <XIcon className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Tên địa điểm *</label>
                <input 
                  required
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                  placeholder="Nhà hát Bến Thành..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Địa chỉ *</label>
                <input 
                  required
                  type="text" 
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                  placeholder="Số 6 Mạc Đĩnh Chi, Q1..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Sức chứa (số lượng ghế) *</label>
                <input 
                  required
                  type="number" 
                  value={formData.capacity}
                  onChange={(e) => setFormData({...formData, capacity: Number(e.target.value)})}
                  className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                />
              </div>
              <div className="pt-4 flex gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="flex-1 px-4 py-2 text-navy-600 bg-navy-50 hover:bg-navy-100 rounded-xl font-medium transition-colors"
                >
                  Huỷ
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 text-white bg-coral-500 hover:bg-coral-600 rounded-xl font-medium transition-colors"
                >
                  Lưu thay đổi
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

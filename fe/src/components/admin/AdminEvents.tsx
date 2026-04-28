import { useState, useEffect } from 'react';
import { Edit2Icon, Trash2Icon, PlusIcon, XIcon } from 'lucide-react';
import { eventApi, venueApi } from '../../services/api';

export function AdminEvents() {
  const [events, setEvents] = useState<any[]>([]);
  const [venues, setVenues] = useState<any[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<any>(null);
  const [formData, setFormData] = useState({ 
    name: '', 
    description: '', 
    image_url: '', 
    category: '',
    venue_id: ''
  });

  const fetchData = async () => {
    try {
      const [evts, vns] = await Promise.all([
        eventApi.getAll(),
        venueApi.getAll()
      ]);
      setEvents(evts);
      setVenues(vns);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingEvent) {
        await eventApi.update(editingEvent.id, formData);
      } else {
        await eventApi.create(formData);
      }
      setIsModalOpen(false);
      setEditingEvent(null);
      setFormData({ name: '', description: '', image_url: '', category: '', venue_id: '' });
      fetchData();
    } catch (error) {
      alert("Lỗi khi lưu sự kiện");
      console.error(error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Bạn có chắc chắn muốn xoá sự kiện này? (Xoá cả lịch diễn và vé)")) {
      try {
        await eventApi.delete(id);
        fetchData();
      } catch (e) {
        alert("Lỗi khi xoá");
        console.error(e);
      }
    }
  };

  const openEditModal = (event: any) => {
    setEditingEvent(event);
    setFormData({ 
      name: event.name, 
      description: event.description || '', 
      image_url: event.image_url || '', 
      category: event.category || '',
      venue_id: event.venue_id
    });
    setIsModalOpen(true);
  };

  const openAddModal = () => {
    setEditingEvent(null);
    setFormData({ name: '', description: '', image_url: '', category: '', venue_id: venues[0]?.id || '' });
    setIsModalOpen(true);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-navy-900">Quản lý Sự kiện</h3>
        <button 
          onClick={openAddModal}
          className="flex items-center gap-2 bg-navy-900 text-white px-4 py-2 rounded-xl hover:bg-navy-800 transition-colors"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Thêm sự kiện</span>
        </button>
      </div>

      <div className="bg-white border border-navy-100 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-navy-50 text-navy-600 font-medium border-b border-navy-100">
            <tr>
              <th className="px-6 py-4">Tên sự kiện</th>
              <th className="px-6 py-4">Thể loại</th>
              <th className="px-6 py-4 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-50">
            {events?.map((e) => (
              <tr key={e.id} className="hover:bg-navy-50/50 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {e.image_url && <img src={e.image_url} alt="img" className="w-10 h-10 rounded-lg object-cover" />}
                    <span className="text-navy-900 font-medium">{e.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 text-navy-600 border-b border-navy-50">{e.category}</td>
                <td className="px-6 py-4 flex items-center justify-end gap-2">
                  <button 
                    onClick={() => openEditModal(e)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Edit2Icon className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDelete(e.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2Icon className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {(!events || events.length === 0) && (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-navy-400">
                  Chưa có dữ liệu sự kiện
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-navy-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center px-6 py-4 border-b border-navy-50">
              <h4 className="text-lg font-bold text-navy-900">
                {editingEvent ? 'Sửa Sự kiện' : 'Thêm Sự kiện mới'}
              </h4>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-navy-400 hover:text-navy-600 transition-colors"
              >
                <XIcon className="w-5 h-5" />
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-navy-700 mb-1">Tên sự kiện *</label>
                  <input 
                    required
                    type="text" 
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-navy-700 mb-1">Thể loại</label>
                  <input 
                    type="text" 
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                    placeholder="Concert, Hài kịch..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-navy-700 mb-1">Địa điểm tổ chức *</label>
                  <select
                    required
                    value={formData.venue_id}
                    onChange={(e) => setFormData({...formData, venue_id: e.target.value})}
                    className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                  >
                    <option value="">-- Chọn địa điểm --</option>
                    {venues.map(v => (
                      <option key={v.id} value={v.id}>{v.name}</option>
                    ))}
                  </select>
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-navy-700 mb-1">Ảnh Banner URL</label>
                  <input 
                    type="text" 
                    value={formData.image_url}
                    onChange={(e) => setFormData({...formData, image_url: e.target.value})}
                    className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                    placeholder="https://..."
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-navy-700 mb-1">Mô tả chi tiết</label>
                  <textarea 
                    rows={4}
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all resize-none"
                  />
                </div>
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

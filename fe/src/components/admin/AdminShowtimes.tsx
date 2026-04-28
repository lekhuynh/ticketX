import { useState, useEffect } from 'react';
import { Edit2Icon, Trash2Icon, PlusIcon, XIcon } from 'lucide-react';
import { showtimeApi, eventApi } from '../../services/api';

export function AdminShowtimes() {
  const [events, setEvents] = useState<any[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string>('');
  const [showtimes, setShowtimes] = useState<any[]>([]);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingShowtime, setEditingShowtime] = useState<any>(null);
  const [formData, setFormData] = useState({ 
    start_time: '', 
    end_time: ''
  });

  useEffect(() => {
    eventApi.getAll().then(data => {
      setEvents(data);
      if (data.length > 0) {
        setSelectedEventId(data[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedEventId) {
      fetchShowtimes(selectedEventId);
    }
  }, [selectedEventId]);

  const fetchShowtimes = async (eventId: string) => {
    try {
      const data = await showtimeApi.getByEventId(eventId);
      setShowtimes(data);
    } catch (e) {
      console.error(e);
      setShowtimes([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        event_id: selectedEventId,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
      };

      if (editingShowtime) {
        await showtimeApi.update(editingShowtime.id, payload);
      } else {
        await showtimeApi.create(payload);
      }
      setIsModalOpen(false);
      setEditingShowtime(null);
      setFormData({ start_time: '', end_time: '' });
      fetchShowtimes(selectedEventId);
    } catch (error) {
      alert("Lỗi khi lưu lịch diễn");
      console.error(error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm("Bạn có chắc chắn muốn xoá lịch diễn này?")) {
      try {
        await showtimeApi.delete(id);
        fetchShowtimes(selectedEventId);
      } catch (e) {
        alert("Lỗi khi xoá");
        console.error(e);
      }
    }
  };

  const formatDateForInput = (isoString: string) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
  };

  const openEditModal = (st: any) => {
    setEditingShowtime(st);
    setFormData({ 
      start_time: formatDateForInput(st.start_time), 
      end_time: formatDateForInput(st.end_time)
    });
    setIsModalOpen(true);
  };

  const openAddModal = () => {
    if (!selectedEventId) {
      alert("Vui lòng chọn sự kiện trước");
      return;
    }
    setEditingShowtime(null);
    setFormData({ start_time: '', end_time: '' });
    setIsModalOpen(true);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-navy-900">Quản lý Lịch diễn</h3>
        
        <div className="flex items-center gap-4">
          <select 
            value={selectedEventId} 
            onChange={(e) => setSelectedEventId(e.target.value)}
            className="px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none max-w-xs"
          >
            {events.map((e) => (
              <option key={e.id} value={e.id}>{e.name}</option>
            ))}
          </select>

          <button 
            onClick={openAddModal}
            className="flex items-center gap-2 bg-navy-900 text-white px-4 py-2 rounded-xl hover:bg-navy-800 transition-colors whitespace-nowrap"
          >
            <PlusIcon className="w-5 h-5" />
            <span>Thêm suất chiếu</span>
          </button>
        </div>
      </div>

      <div className="bg-white border border-navy-100 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-navy-50 text-navy-600 font-medium border-b border-navy-100">
            <tr>
              <th className="px-6 py-4">Bắt đầu</th>
              <th className="px-6 py-4">Kết thúc</th>
              <th className="px-6 py-4 text-right">Thao tác</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-navy-50">
            {showtimes?.map((st) => (
              <tr key={st.id} className="hover:bg-navy-50/50 transition-colors">
                <td className="px-6 py-4 text-navy-900 font-medium">
                  {new Date(st.start_time).toLocaleString('vi-VN')}
                </td>
                <td className="px-6 py-4 text-navy-600">
                  {new Date(st.end_time).toLocaleString('vi-VN')}
                </td>
                <td className="px-6 py-4 flex items-center justify-end gap-2">
                  <button 
                    onClick={() => openEditModal(st)}
                    className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  >
                    <Edit2Icon className="w-4 h-4" />
                  </button>
                  <button 
                    onClick={() => handleDelete(st.id)}
                    className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  >
                    <Trash2Icon className="w-4 h-4" />
                  </button>
                </td>
              </tr>
            ))}
            {(!showtimes || showtimes.length === 0) && (
              <tr>
                <td colSpan={3} className="px-6 py-8 text-center text-navy-400">
                  Chưa có lịch diễn nào cho sự kiện này
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-navy-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden">
            <div className="flex justify-between items-center px-6 py-4 border-b border-navy-50">
              <h4 className="text-lg font-bold text-navy-900">
                {editingShowtime ? 'Sửa Lịch diễn' : 'Thêm Lịch diễn mới'}
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
                <label className="block text-sm font-medium text-navy-700 mb-1">Thời gian bắt đầu *</label>
                <input 
                  required
                  type="datetime-local" 
                  value={formData.start_time}
                  onChange={(e) => setFormData({...formData, start_time: e.target.value})}
                  className="w-full px-4 py-2 border border-navy-200 rounded-xl focus:ring-2 focus:ring-coral-500/20 focus:border-coral-500 outline-none transition-all"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-navy-700 mb-1">Thời gian kết thúc *</label>
                <input 
                  required
                  type="datetime-local" 
                  value={formData.end_time}
                  onChange={(e) => setFormData({...formData, end_time: e.target.value})}
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

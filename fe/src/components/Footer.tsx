import React from 'react';
import { TicketIcon } from 'lucide-react';
export function Footer() {
  return (
    <footer className="bg-navy-900 text-navy-200 py-16 border-t border-navy-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center gap-2 mb-6">
              <div className="bg-coral-500 text-white p-1.5 rounded-lg">
                <TicketIcon className="w-5 h-5" />
              </div>
              <span className="font-heading font-bold text-xl text-white tracking-tight">
                Ve<span className="text-coral-500">Nhanh</span>
              </span>
            </div>
            <p className="text-sm leading-relaxed mb-6">
              Nền tảng đặt vé sự kiện hàng đầu Việt Nam. Mang đến trải nghiệm
              mua vé dễ dàng, an toàn và nhanh chóng nhất.
            </p>
          </div>

          <div>
            <h4 className="text-white font-heading font-semibold mb-6">
              Về chúng tôi
            </h4>
            <ul className="space-y-3 text-sm">
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Giới thiệu
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Tuyển dụng
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Liên hệ
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-heading font-semibold mb-6">
              Hỗ trợ
            </h4>
            <ul className="space-y-3 text-sm">
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Trung tâm trợ giúp
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Hướng dẫn đặt vé
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Chính sách hoàn tiền
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Câu hỏi thường gặp
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-heading font-semibold mb-6">
              Pháp lý
            </h4>
            <ul className="space-y-3 text-sm">
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Điều khoản sử dụng
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Chính sách bảo mật
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-coral-400 transition-colors">
                  Quy chế hoạt động
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-navy-800 text-sm text-center flex flex-col md:flex-row justify-between items-center gap-4">
          <p>&copy; 2025 VeNhanh. Tất cả quyền được bảo lưu.</p>
          <div className="flex gap-4">
            <span className="w-8 h-8 rounded-full bg-navy-800 flex items-center justify-center hover:bg-coral-500 transition-colors cursor-pointer text-white">
              FB
            </span>
            <span className="w-8 h-8 rounded-full bg-navy-800 flex items-center justify-center hover:bg-coral-500 transition-colors cursor-pointer text-white">
              IG
            </span>
            <span className="w-8 h-8 rounded-full bg-navy-800 flex items-center justify-center hover:bg-coral-500 transition-colors cursor-pointer text-white">
              YT
            </span>
          </div>
        </div>
      </div>
    </footer>);

}
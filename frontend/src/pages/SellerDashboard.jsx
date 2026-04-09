import { useState, useEffect } from "react";

import { ShoppingCart, Car, TrendingUp, Clock, ChevronDown } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import moment from "moment";
import { toast } from "sonner";
import StatCard from "../components/StatCard";

const statusConfig = {
  "Pendente": "bg-yellow-100 text-yellow-700",
  "Confirmado": "bg-blue-100 text-blue-700",
  "Em Produção": "bg-purple-100 text-purple-700",
  "Pronto para Entrega": "bg-emerald-100 text-emerald-700",
  "Entregue": "bg-green-100 text-green-700",
  "Cancelado": "bg-red-100 text-red-700",
};

const allStatuses = ["Pendente", "Confirmado", "Em Produção", "Pronto para Entrega", "Entregue", "Cancelado"];

export default function SellerDashboard() {
  const [orders, setOrders] = useState([]);
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState("Todos");

  useEffect(() => {
    async function load() {
      const [o, v] = await Promise.all([
        autoelite.entities.Order.list("-created_date", 200),
        autoelite.entities.Vehicle.list("-created_date", 200),
      ]);
      setOrders(o);
      setVehicles(v);
      setLoading(false);
    }
    load();
  }, []);

  const updateOrderStatus = async (orderId, newStatus) => {
    await autoelite.entities.Order.update(orderId, { status: newStatus });
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: newStatus } : o));
    toast.success(`Status atualizado para "${newStatus}"`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const revenue = orders.filter(o => o.status === "Entregue").reduce((s, o) => s + (o.total_price || 0), 0);
  const activeOrders = orders.filter(o => !["Entregue", "Cancelado"].includes(o.status));

  const filtered = filterStatus === "Todos" ? orders : orders.filter(o => o.status === filterStatus);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl font-bold text-foreground">Painel do Vendedor</h1>
          <p className="text-muted-foreground mt-1">Gerencie pedidos e acompanhe o desempenho.</p>
        </div>
        <div className="hidden md:block bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-full">
          VENDEDOR
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={ShoppingCart} label="Total de Pedidos" value={orders.length} />
        <StatCard icon={Clock} label="Pedidos Ativos" value={activeOrders.length} />
        <StatCard icon={Car} label="Veículos no Catálogo" value={vehicles.length} />
        <StatCard
          icon={TrendingUp}
          label="Receita (Entregues)"
          value={new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(revenue)}
        />
      </div>

      {/* Orders Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="p-5 border-b border-border flex flex-col md:flex-row md:items-center justify-between gap-3">
          <h2 className="font-semibold text-foreground">Gerenciamento de Pedidos</h2>
          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-full md:w-44">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Todos">Todos</SelectItem>
              {allStatuses.map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}
            </SelectContent>
          </Select>
        </div>

        {filtered.length === 0 ? (
          <div className="p-12 text-center text-muted-foreground">Nenhum pedido encontrado.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-muted-foreground">
                <tr>
                  <th className="text-left px-5 py-3 font-medium">Pedido</th>
                  <th className="text-left px-5 py-3 font-medium">Cliente</th>
                  <th className="text-left px-5 py-3 font-medium">Veículo</th>
                  <th className="text-left px-5 py-3 font-medium">Valor</th>
                  <th className="text-left px-5 py-3 font-medium">Data</th>
                  <th className="text-left px-5 py-3 font-medium">Status</th>
                  <th className="text-left px-5 py-3 font-medium">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map(order => (
                  <tr key={order.id} className="hover:bg-muted/30 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-xs text-muted-foreground">
                      #{order.id?.slice(-6)}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-foreground">{order.customer_name}</div>
                      <div className="text-xs text-muted-foreground">{order.customer_email}</div>
                    </td>
                    <td className="px-5 py-3.5 font-medium text-foreground">{order.vehicle_name}</td>
                    <td className="px-5 py-3.5 font-semibold text-primary">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(order.total_price)}
                    </td>
                    <td className="px-5 py-3.5 text-muted-foreground">
                      {moment(order.created_date).format("DD/MM/YY")}
                    </td>
                    <td className="px-5 py-3.5">
                      <Badge className={cn("text-xs", statusConfig[order.status])}>
                        {order.status}
                      </Badge>
                    </td>
                    <td className="px-5 py-3.5">
                      <Select value={order.status} onValueChange={(v) => updateOrderStatus(order.id, v)}>
                        <SelectTrigger className="h-8 text-xs w-40">
                          <SelectValue />
                          <ChevronDown className="w-3 h-3 ml-1" />
                        </SelectTrigger>
                        <SelectContent>
                          {allStatuses.map(s => (
                            <SelectItem key={s} value={s} className="text-xs">{s}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Vehicle Status Summary */}
      <div className="bg-card rounded-xl border border-border p-5">
        <h2 className="font-semibold text-foreground mb-4">Status do Inventário</h2>
        <div className="grid grid-cols-3 gap-4">
          {["Disponível", "Reservado", "Vendido"].map(status => (
            <div key={status} className="text-center">
              <p className="text-3xl font-bold text-foreground">
                {vehicles.filter(v => (v.status || "Disponível") === status).length}
              </p>
              <p className="text-sm text-muted-foreground mt-1">{status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
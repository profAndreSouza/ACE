import { useState, useEffect } from "react";

import { Link } from "react-router-dom";
import { Car, ShoppingCart, TrendingUp, Clock, ArrowRight } from "lucide-react";
import StatCard from "../components/StatCard";
import VehicleCard from "../components/VehicleCard";
import OrderCard from "../components/OrderCard";

export default function Dashboard() {
  const [vehicles, setVehicles] = useState([]);
  const [orders, setOrders] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      const [v, o, u] = await Promise.all([
        autoelite.entities.Vehicle.list("-created_date", 4),
        autoelite.entities.Order.list("-created_date", 3),
        autoelite.auth.me(),
      ]);
      setVehicles(v);
      setOrders(o);
      setUser(u);
      setLoading(false);
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const availableVehicles = vehicles.filter(v => v.status === "Disponível" || !v.status).length;
  const activeOrders = orders.filter(o => o.status !== "Entregue" && o.status !== "Cancelado").length;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground">
          Olá, {user?.full_name?.split(" ")[0] || "Cliente"} 👋
        </h1>
        <p className="text-muted-foreground mt-1">Bem-vindo à sua concessionária digital.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Car} label="Veículos Disponíveis" value={availableVehicles} />
        <StatCard icon={ShoppingCart} label="Pedidos Ativos" value={activeOrders} />
        <StatCard icon={TrendingUp} label="Total de Veículos" value={vehicles.length} />
        <StatCard icon={Clock} label="Seus Pedidos" value={orders.filter(o => o.customer_email === user?.email).length} />
      </div>

      {/* Recent Vehicles */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-xl font-semibold text-foreground">Veículos em Destaque</h2>
          <Link to="/veiculos" className="text-sm text-primary font-medium hover:underline flex items-center gap-1">
            Ver todos <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        {vehicles.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {vehicles.map(v => <VehicleCard key={v.id} vehicle={v} />)}
          </div>
        ) : (
          <div className="bg-card rounded-xl border border-border p-12 text-center">
            <Car className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">Nenhum veículo cadastrado ainda.</p>
          </div>
        )}
      </div>

      {/* Recent Orders */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-xl font-semibold text-foreground">Pedidos Recentes</h2>
          <Link to="/pedidos" className="text-sm text-primary font-medium hover:underline flex items-center gap-1">
            Ver todos <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        {orders.length > 0 ? (
          <div className="space-y-3">
            {orders.map(o => <OrderCard key={o.id} order={o} />)}
          </div>
        ) : (
          <div className="bg-card rounded-xl border border-border p-12 text-center">
            <ShoppingCart className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">Nenhum pedido realizado ainda.</p>
          </div>
        )}
      </div>
    </div>
  );
}
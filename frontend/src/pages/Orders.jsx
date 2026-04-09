import { useState, useEffect } from "react";

import { ShoppingCart } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import OrderCard from "../components/OrderCard";

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("all");

  useEffect(() => {
    async function load() {
      const data = await autoelite.entities.Order.list("-created_date", 100);
      setOrders(data);
      setLoading(false);
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-muted border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const filtered = tab === "all" 
    ? orders 
    : tab === "active" 
      ? orders.filter(o => !["Entregue", "Cancelado"].includes(o.status))
      : orders.filter(o => o.status === "Entregue");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl font-bold text-foreground">Meus Pedidos</h1>
        <p className="text-muted-foreground mt-1">Acompanhe todos os seus pedidos de veículos.</p>
      </div>

      <Tabs value={tab} onValueChange={setTab}>
        <TabsList>
          <TabsTrigger value="all">Todos ({orders.length})</TabsTrigger>
          <TabsTrigger value="active">Ativos ({orders.filter(o => !["Entregue", "Cancelado"].includes(o.status)).length})</TabsTrigger>
          <TabsTrigger value="completed">Entregues ({orders.filter(o => o.status === "Entregue").length})</TabsTrigger>
        </TabsList>
      </Tabs>

      {filtered.length > 0 ? (
        <div className="space-y-3">
          {filtered.map(o => <OrderCard key={o.id} order={o} />)}
        </div>
      ) : (
        <div className="bg-card rounded-xl border border-border p-16 text-center">
          <ShoppingCart className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-semibold text-foreground mb-1">Nenhum pedido encontrado</h3>
          <p className="text-sm text-muted-foreground">Seus pedidos aparecerão aqui.</p>
        </div>
      )}
    </div>
  );
}
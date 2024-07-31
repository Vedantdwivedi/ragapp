import { useQuery } from "react-query"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { getServices, startService, stopService, removeService } from "@/client/service";
import { Service } from "@/client/models/service";
import { TbFilePencil, TbPlayerPauseFilled, TbPlayerPlayFilled } from "react-icons/tb";
import { ImSpinner8 } from "react-icons/im";
import { TiDeleteOutline } from "react-icons/ti";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "../ui/alert-dialog";

import { useEffect, useState } from "react";
import { CreateAgentDialog } from "./createAgent";
import { TooltipProvider } from "@radix-ui/react-tooltip";
import { Tooltip, TooltipContent, TooltipTrigger } from "../ui/tooltip";

function AlertDialogRemoveApp({
    service,
    refetch
}: {
    service: Service,
    refetch: () => void
}) {

    async function handleRemoveService() {
        await removeService(service.id);
        refetch();
    }

    return (
        <AlertDialog>
            <AlertDialogTrigger asChild>
                <Button variant="ghost"><TiDeleteOutline size={20} /></Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>Remove {service.app_name}?</AlertDialogTitle>
                    <AlertDialogDescription>
                        All the data and the configuration will be removed. Are you really sure you want to delete this app?
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={handleRemoveService}>
                        Ok
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    )
}

function StartStopButton({
    service,
    refetch
}: {
    service: Service,
    refetch: () => void
}) {
    const [isHandling, setIsHandling] = useState(false);

    async function handleStopService() {
        setIsHandling(true);
        await stopService(service.id);
        refetch();
        setIsHandling(false);
    }

    async function handleStartService() {
        setIsHandling(true);
        await startService(service.id);
        refetch();
        setIsHandling(false);
    }

    return (
        service.status === "running"
            ? (<Button
                variant="outline"
                className="flex items-center text-muted-foreground"
                onClick={handleStopService}
                disabled={isHandling}
            >
                <TbPlayerPauseFilled size={20} />
            </Button>)
            : (<Button
                variant="outline"
                className="flex items-center text-muted-foreground"
                onClick={handleStartService}
                disabled={isHandling}
            >
                <TbPlayerPlayFilled size={20} />
            </ Button>)
    )
}

function ServiceCard({
    service,
    refetch
}: {
    service: Service,
    refetch: () => void
}) {

    return (
        <TooltipProvider>
            <Card key={service.id} className="shadow-md">
                <CardHeader className="flex flex-row justify-between">
                    <CardTitle className="text-xl font-bold flex items-center text-foreground">
                        <a
                            href={service.url}
                            target="_blank"
                        >
                            {service.app_name ? service.app_name : service.name}
                        </a>
                    </CardTitle>
                    <AlertDialogRemoveApp service={service} refetch={refetch} />
                </CardHeader>
                <CardContent>
                    <p className="text-foreground">State: {" "}
                        {
                            service.status === "running"
                                ? (
                                    <Tooltip>
                                        <TooltipTrigger>
                                            <span className="text-green">Running</span>
                                        </TooltipTrigger>
                                        <TooltipContent side="right">
                                            <span>since {service.started_at}</span>
                                        </TooltipContent>
                                    </Tooltip>
                                )
                                : <span className="text-red">Stopped</span>
                        }
                    </p>
                </CardContent>
                <CardFooter className="flex justify-between">
                    <a
                        className="text-primary-foreground"
                        href={`${service.url}/admin/`}
                        target="_blank"
                    >
                        <Button variant="outline" className="flex items-center text-muted-foreground">
                            <TbFilePencil size={20} />
                            Edit
                        </Button>
                    </a>
                    <StartStopButton service={service} refetch={refetch} />
                </CardFooter>
            </Card>
        </TooltipProvider>
    )
}


export function ServicesList() {
    const { data, error, isLoading, refetch } = useQuery('services', getServices);
    const [addAgentDialogOpen, setAddAgentDialogOpen] = useState(false);

    useEffect(() => {
        if (!addAgentDialogOpen) {
            refetch();
        }
    }, [addAgentDialogOpen]);

    return (
        <>
            <header className="mb-8 space-y-2">
                <h1 className="text-3xl font-bold text-foreground">
                    Agents
                </h1>
                <CreateAgentDialog
                    open={addAgentDialogOpen}
                    setOpen={setAddAgentDialogOpen}
                />
                <Button onClick={() => setAddAgentDialogOpen(true)}>+ New Agent</Button>
            </header>
            <section className="space-y-4">
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2 pr-8">
                    {
                        isLoading
                            ? <div className="flex justify-center animate-spin items-start w-10"><ImSpinner8 /></div>
                            : (
                                data?.map(service => (
                                    <ServiceCard service={service} refetch={refetch} />
                                ))
                            )
                    }
                </div>
            </section>
        </>
    )
}


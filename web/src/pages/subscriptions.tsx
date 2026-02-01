import { UrlInput } from "@/components/common/url-input";
import { SubscriptionsTable } from "@/features/subscriptions/subscriptions-table";
import { useSubscriptions } from "@/features/subscriptions/use-subscriptions";
import { useCountdown } from "@/hooks/use-countdown";
import { isValidUrl } from "@/lib/url";
import { Button, Card, CardBody, NumberInput, Tooltip } from "@heroui/react";
import {
  ClockIcon,
  HashIcon,
  ListMusicIcon,
  RefreshCwIcon,
  RssIcon,
} from "lucide-react";
import { useState } from "react";

const DEFAULT_MAX_ITEMS = 100;

export function SubscriptionsPage() {
  const [url, setUrl] = useState("");
  const [maxItems, setMaxItems] = useState(DEFAULT_MAX_ITEMS);
  const [isAdding, setIsAdding] = useState(false);
  const {
    subscriptions,
    schedulerStatus,
    isLoading,
    addSubscription,
    updateSubscription,
    deleteSubscription,
    syncSubscription,
    syncAll,
  } = useSubscriptions();
  const [isSyncing, setIsSyncing] = useState(false);

  const canAdd = isValidUrl(url);
  const isEmpty = subscriptions.length == 0;

  const handleAdd = async () => {
    if (!canAdd) return;
    setIsAdding(true);
    const success = await addSubscription(url.trim(), maxItems);
    if (success) {
      setUrl("");
    }
    setIsAdding(false);
  };

  const handleToggleEnabled = async (id: string, enabled: boolean) => {
    await updateSubscription(id, { enabled });
  };

  const handleSyncAll = async () => {
    setIsSyncing(true);
    await syncAll();
    setIsSyncing(false);
  };

  const nextSyncTime = schedulerStatus?.next_run_at
    ? new Date(schedulerStatus.next_run_at)
    : null;
  const countdown = useCountdown(nextSyncTime);
  const enabledCount = subscriptions.filter((s) => s.enabled).length;
  const totalCount = subscriptions.length;

  return (
    <>
      {/* Page Title */}
      <h1 className="text-foreground mb-5 text-2xl font-bold">My playlists</h1>

      {/* URL Input Section */}
      <section className="mb-4 flex gap-2">
        <div className="flex-1">
          <UrlInput
            value={url}
            onChange={setUrl}
            disabled={isAdding}
            placeholder="Playlist URL to sync automatically"
          />
        </div>
        <Tooltip content="Max tracks to sync per run" offset={14}>
          <NumberInput
            hideStepper
            variant="faded"
            value={maxItems}
            onValueChange={setMaxItems}
            minValue={1}
            maxValue={10000}
            radius="lg"
            fullWidth={false}
            formatOptions={{
              useGrouping: false,
            }}
            placeholder="Max"
            startContent={<HashIcon className="text-foreground-400 h-4 w-4" />}
            className="w-20 font-mono"
          />
        </Tooltip>
        <Button
          color="primary"
          radius="lg"
          variant={canAdd ? "shadow" : "solid"}
          className="shadow-primary-100/50"
          onPress={handleAdd}
          isDisabled={!canAdd}
          isLoading={isAdding}
          startContent={!isAdding && <RssIcon className="h-4 w-4" />}
        >
          Subscribe
        </Button>
      </section>

      {/* Stats Cards */}
      <div className="mb-4 grid grid-cols-3 gap-3">
        {/* Active playlists */}
        <Card>
          <CardBody className="flex-row items-center gap-3 py-3">
            <div className="bg-secondary/10 rounded-lg p-2">
              <ListMusicIcon className="text-secondary h-[18px] w-[18px]" />
            </div>
            <div>
              <p className="text-default-500 text-xs tracking-wide uppercase">
                Active
              </p>
              <p className="text-lg font-semibold">
                {enabledCount}
                <span className="text-default-400 text-sm font-normal">
                  /{totalCount}
                </span>
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Next sync */}
        <Card>
          <CardBody className="flex-row items-center gap-3 py-3">
            <div className="bg-success/10 rounded-lg p-2">
              <ClockIcon className="text-success h-[18px] w-[18px]" />
            </div>
            <div>
              <p className="text-default-500 text-xs tracking-wide uppercase">
                Next Sync
              </p>
              <p className="text-success font-mono text-lg font-semibold">
                {countdown}
              </p>
            </div>
          </CardBody>
        </Card>

        {/* Sync all button */}
        <Card
          as={Button}
          isPressable
          isDisabled={isSyncing || isEmpty}
          onPress={handleSyncAll}
          className="bg-default-100 border-default-200 hover:bg-default-200 border transition-colors"
        >
          <CardBody className="flex-row items-center justify-center gap-2 py-3">
            <RefreshCwIcon
              className={`text-default-500 h-[18px] w-[18px] ${isSyncing ? "animate-spin" : ""}`}
            />
            <span className="text-default-600 font-medium">
              {isSyncing ? "Syncing..." : "Sync All"}
            </span>
          </CardBody>
        </Card>
      </div>

      {/* Subscriptions Table */}
      <SubscriptionsTable
        subscriptions={subscriptions}
        isLoading={isLoading}
        onToggleEnabled={handleToggleEnabled}
        onSync={syncSubscription}
        onDelete={deleteSubscription}
      />
    </>
  );
}
